#!/usr/bin/env python

import argparse
import datetime
import getpass
import glob
import os
import random
import re
import string
import sys
from xml.etree import ElementTree

import yaml


BREAK_LENGTH = 15
HIGH_TOLERANCE = 15
IGNORED_SCENARIO_CLASSES = (
    'eFreeRoamScenarioClass',
    'eTemplateScenarioClass',
    'eTutorialScenarioClass',
)
LOW_TOLERANCE = 15
TEMPLATE_BOILERPLATE = """<!DOCTYPE html>
<!--[if lt IE 7]>      <html class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>         <html class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>         <html class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js"> <!--<![endif]-->
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <title>Railworks Dispatcher Work Order #${shift_number}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="file://${dispatcher_artwork_folder}/main.css">
    </head>
    <body>
        ${orders}
        <script type="application/javascript" src="file://${dispatcher_artwork_folder}/build.js"></script>
    </body>
</html>"""
TEMPLATE_WORK_ORDER = """
    <article class="${scenario_class}">
        <div class="collapsible">
            <img class="logo" src="file://${dispatcher_artwork_folder}/Logos/${logo}" alt="">
            <div>Driver ${username}</div>
            <div class="larger">Shift ${shift_number}</div>
        </div>
        <h1>${scenario_name}</h1>
        <div class="collapsible">
            <div class="larger">${scenario_description}</div>
            <div class="with-margin">${scenario_briefing}</div>
            <div class="with-margin">Printed ${date} at ${scenario_start_location}</div>
        </div>
    </article>
"""


def die(message='', code=1):
    if message:
        print(message, file=sys.stderr)
    sys.exit(code)


def humanize_username(username):
    SPLITTERS = '.-'
    IGNORED = '0123456789'  # @TODO: remove funny chars from usernames
    for splitter in SPLITTERS.split():
        username = ' '.join(username.split(splitter))
    username = username.capitalize()
    return username


def ensure_folder(path):
    try:
        os.makedirs(path)
        return True
    except OSError:
        return False


def get_arwork_for_date(artwork_dict, date):
    for artwork in artwork_dict:
        lo, hi = artwork.get('from'), artwork.get('until')
        if lo:
            lo_dt = datetime.datetime.combine(lo, datetime.time())
            if date < lo_dt:
                continue
        if hi:
            hi_dt = datetime.datetime.combine(hi, datetime.time()) + datetime.timedelta(days=1)
            if date >= hi_dt:
                continue
        return artwork['logo']


def get_last_number(work_orders_folder):
    pattern = os.path.join(work_orders_folder, '????.html')
    all_htmls = sorted(glob.glob(pattern))
    if not all_htmls:
        return 0
    last_file = os.path.split(all_htmls[-1])[1]
    last_number = int(last_file.split('.')[0])
    return last_number


def int_to_time(int_time):
    HOUR = 3600
    hours = int(int_time / HOUR)
    minutes = int((int_time % HOUR) / 60)
    return hours, minutes


def launch_html(path):
    try:
        os.startfile(path)
    except AttributeError:
        os.system('xdg-open \'%s\'' % path)


# @TODO: put this in a class
def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('work_orders', default=1, nargs='?')
    return parser.parse_args(args)


def render_html(context):
    return string.Template(TEMPLATE_BOILERPLATE).safe_substitute(**context)


def render_work_order(context):
    return string.Template(TEMPLATE_WORK_ORDER).safe_substitute(**context)


def to_minutes(time_string):
    pattern = re.compile('(?P<inte>[0-9\.]{1,4})(?P<stri>[hm]{1})')
    try:
        i, s = pattern.match(time_string).groups()
        minutes = float(i) * 60 if s == 'h' else i
        return int(minutes)
    except AttributeError:
        raise ValueError('Value %s does not meet the expected format.' % time_string)


def main():

    complete_order_count = 0
    """
    How many work orders were generated
    """
    complete_order_duration = 0
    """
    How many minutes will generated work orders take
    """

    needed_order_count = None
    """
    How many work orders should be generated
    """
    needed_order_duration_span = None
    """
    How many minutes should work orders take
    """

    default_route_config = None
    """
    Route artwork config to use when given route is not present in route_configs
    """
    route_configs = None
    """
    A dictionary of route artwork configs, indexed by route name
    """

    railworks_folder = os.getcwd()
    scenario_folders = os.path.join(railworks_folder,
                                    'Content', 'Routes', '*', 'Scenarios', '*', 'ScenarioProperties.xml')
    work_orders_folder = os.path.join(railworks_folder, 'WorkOrders')
    ensure_folder(work_orders_folder)

    dispatcher_folder = os.path.abspath(os.path.dirname(__file__))
    dispatcher_data_folder = os.path.join(dispatcher_folder, 'Dispatcher')

    args = parse_args(sys.argv[1:])
    try:
        order_minutes = to_minutes(args.work_orders)
        # if we set min duration to 1 minute, orders with incorrectly set duration of 0 will be left out
        needed_order_duration_span = (max(order_minutes - LOW_TOLERANCE, 1), order_minutes + HIGH_TOLERANCE)
    except (TypeError, ValueError):
        needed_order_count = int(args.work_orders)

    orders_html = []
    all_scenarios = glob.glob(scenario_folders)
    random.shuffle(all_scenarios)

    if not all_scenarios:
        die('No scenarios found. Are you sure you are running dispatcher from the correct folder?')

    with open(os.path.join(dispatcher_data_folder, 'artwork.yaml')) as f:
        route_config_yaml = yaml.load(f)
    default_route_config = route_config_yaml.pop('Default')
    route_configs = route_config_yaml

    template_context = {
        'dispatcher_artwork_folder': os.path.join(dispatcher_data_folder, 'Artwork'),
        'username': humanize_username(getpass.getuser()),
    }

    def should_continue(count, duration):
        if needed_order_count is not None:
            return count < needed_order_count
        else:
            return not(needed_order_duration_span[0] < duration < needed_order_duration_span[1])

    while all_scenarios and should_continue(complete_order_count, complete_order_duration):

        shift_number = str(get_last_number(work_orders_folder) + complete_order_count + 1).zfill(4)

        todays_work_order = all_scenarios[-1]
        all_scenarios.pop()

        # only allow scenarios from existing unpacked routes
        scenario_folder_suffix = os.path.join(*todays_work_order.split(os.sep)[-3:])
        route_folder = todays_work_order.replace(scenario_folder_suffix, '')
        route_description = os.path.join(route_folder, 'RouteProperties.xml')
        if not os.path.exists(route_description):
            continue

        xml = ElementTree.parse(todays_work_order)

        scenario_class = xml.find('./ScenarioClass').text
        if scenario_class in IGNORED_SCENARIO_CLASSES:
            continue

        scenario_duration = int(xml.find('./DurationMins').text)
        if (needed_order_duration_span is not None and
            complete_order_duration + scenario_duration > needed_order_duration_span[1]):
            continue

        scenario_name = xml.find('./DisplayName/Localisation-cUserLocalisedString/English').text
        scenario_description = xml.find('./Description/Localisation-cUserLocalisedString/English').text
        scenario_briefing = xml.find('./Briefing/Localisation-cUserLocalisedString/English').text

        scenario_start_location = xml.find('./StartLocation/Localisation-cUserLocalisedString/English').text
        scenario_start_time = xml.find('./StartTime').text
        scenario_start_day = xml.find('./StartDD').text
        scenario_start_month = xml.find('./StartMM').text
        scenario_start_year = xml.find('./StartYYYY').text

        time = int_to_time(int(scenario_start_time))
        time_adjust = random.randrange(15, 45)
        date = datetime.datetime(
            int(scenario_start_year), int(scenario_start_month), int(scenario_start_day),
            *time
        ) - datetime.timedelta(minutes=time_adjust)

        xml = ElementTree.parse(route_description)
        route_name = xml.find('./DisplayName/Localisation-cUserLocalisedString/English').text
        route_artwork = route_configs.get(route_name, default_route_config)
        logo = get_arwork_for_date(route_artwork, date)

        template_context.update({
            'logo': logo,
            'scenario_name': scenario_name,
            'scenario_description': scenario_description,
            'scenario_briefing': scenario_briefing,
            'scenario_class': scenario_class,
            'shift_number': shift_number,
        })

        # only calculate start date and location for the very first work order
        if complete_order_count == 0:
            template_context.update({
                'date': date,
                'scenario_start_location': scenario_start_location or 'Depot',
            })

        orders_html.append(render_work_order(template_context))

        complete_order_count += 1
        complete_order_duration += int(scenario_duration) + BREAK_LENGTH

    if not complete_order_count:
        die('Not able to generate any scenario meeting your requirements. Sorry.')

    last_work_order_number = str(get_last_number(work_orders_folder) + complete_order_count).zfill(4)

    template_context.update({'orders': "\n".join(orders_html)})
    html = render_html(template_context)

    html_name = last_work_order_number + '.html'
    html_path = os.path.join(work_orders_folder, html_name)
    open(html_path, 'w').write(html)
    launch_html(html_path)


if __name__ == '__main__':
    main()
