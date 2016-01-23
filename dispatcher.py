#!/usr/bin/env python
# coding: utf-8

import argparse
import datetime
import glob
import itertools
import json
import logging
import os
import random
import re
import steam
import subprocess
import sys
import urllib.error

import jinja2
import xmltodict
import yaml


BREAK_LENGTH = 15
HIGH_TOLERANCE = 15
IGNORED_ROUTES = (
    'Academy',
    'TestTraK',
)
IGNORED_SCENARIO_CLASSES = (
    'eFreeRoamScenarioClass',
    'eTemplateScenarioClass',
    'eTutorialScenarioClass',
)
LOW_TOLERANCE = 15
STEAM_API_KEY = 'E0668EFB2DCED5DAAEFDAEA751B029DD'
TEMPLATE_CONFIG = """
# Automatically created by Railworks Dispatcher
# See https://github.com/centralniak/railworks-dispatcher
# for instructions how to configure your Railworks Dispatcher instance

steam:
  profile: ~
  hours_two_weeks: 14
"""


class DriverInstruction(object):

    data = None
    start_datetime = None

    def __init__(self, data, start_datetime):
        self.data = data
        self.start_datetime = start_datetime

    @property
    def arrival(self):
        duration = int(float(self.data['Duration']['#text']))
        seconds_after_start = float(self.data['DueTime']['#text'])
        if not seconds_after_start or not duration:
            return
        arrival = self.start_datetime + datetime.timedelta(seconds=seconds_after_start - duration)
        return arrival

    @property
    def departure(self):
        seconds_after_start = float(self.data['DueTime']['#text'])
        if not seconds_after_start:
            return
        return self.start_datetime + datetime.timedelta(seconds=seconds_after_start)

    @property
    def extra(self):
        operation = self.data['Operation']['#text'].lower()
        if operation != 'Default':
            return getattr(self, 'operation_' + operation)

    @property
    def location(self):
        try:
            return self.data['DisplayName']['#text']
        except TypeError:
            logging.debug('Unable to fetch driver instruction location')
            logging.debug(json.dumps(self.data, indent=4))
            return ''

    @property
    def operation_addtoback(self):
        cars = self.data['RailVehicleNumber']['e']
        if not isinstance(cars, list):
            cars = [cars]
        return 'Attach {0}'.format(', '.join([c['#text'] for c in cars]))

    @property
    def operation_dropoffrailvehicle(self):
        cars = self.data['RailVehicleNumber']['e']
        if not isinstance(cars, list):
            cars = [cars]
        return 'Detach {0}'.format(', '.join([c['#text'] for c in cars]))

    @property
    def stopping(self):
        try:
            return (
                self.data['PickingUp']['#text'] == '1' and
                self.data['Waypoint']['#text'] == '0') \
                and self.data['MinSpeed']['#text'] == '0'
        except KeyError:
            return False


class Route(object):

    data = None

    def __init__(self, xml):
        self.data = xmltodict.parse(open(xml, encoding='utf-8').read())['cRouteProperties']

    @property
    def name(self):
        return self.data['DisplayName']['Localisation-cUserLocalisedString']['English']['#text']

    @property
    def uuids(self):
        return [
            e['#text'] for e in self.data['ID']['cGUID']['UUID']['e']
        ]


class Scenario(object):

    basic_data = None
    detailed_data = None
    route_xml = None

    debug_filenames = None

    def __init__(self, xml_basic, xml_detailed, xml_route):
        self.basic_data = xmltodict.parse(open(xml_basic, encoding='utf-8').read())['cScenarioProperties']
        self.detailed_data = xmltodict.parse(open(xml_detailed, encoding='utf-8').read())['cRecordSet']['Record']
        self.route_xml = xml_route
        self.debug_filenames = [xml_route, xml_basic, xml_detailed]

    def __unicode__(self):
        return '{}: {}'.format(self.devstring, self.name)

    @property
    def briefing(self):
        try:
            briefing = self.basic_data['Briefing']['Localisation-cUserLocalisedString']['English']['#text']
            if briefing == self.description:
                return ''
            return briefing
        except KeyError:
            return ''

    @property
    def description(self):
        try:
            return self.basic_data['Description']['Localisation-cUserLocalisedString']['English']['#text']
        except KeyError:
            return ''

    @property
    def devstring(self):
        return self.basic_data['ID']['cGUID']['DevString']['#text']

    @property
    def driver_instructions(self):
        if self.player_service is None:
            return []

        all_instructions = self.player_service['Driver']['cDriver']['DriverInstructionContainer']['cDriverInstructionContainer']['DriverInstruction']
        return_instructions = []
        for instruction_type in all_instructions:
            if instruction_type in ['cTriggerInstruction']:
                continue
            current_instruction_type = all_instructions[instruction_type]

            # handle case when only one element of given type is provided
            # (xmltodict does not return treat this as a list then)
            if not isinstance(current_instruction_type, list):
                current_instruction_type = [current_instruction_type]

            # @TODO: actually, per each type there might be multiple - rewrite!
            for instructions in current_instruction_type:
                instructions = instructions['DeltaTarget']['cDriverInstructionTarget']
                if not isinstance(instructions, list):
                    instructions = [instructions]

                for instruction in instructions:
                    instruction = DriverInstruction(instruction, self.start_datetime)
                    if instruction.location and (instruction.arrival or instruction.departure):
                        return_instructions.append(instruction)

        return sorted(return_instructions, key=lambda i: i.departure)

    @property
    def duration(self):
        try:
            return int(self.basic_data['DurationMins']['#text'])
        except (TypeError, IndexError):
            return 0

    @property
    def formation(self):
        # for some reason this is usually flipped
        initial_rv = self.player_service['Driver']['cDriver']['InitialRV']['e']
        if not isinstance(initial_rv, list):
            initial_rv = [initial_rv]
        try:
            return [c['#text'] for c in initial_rv[::-1]]
        except TypeError:
            return []

    @property
    def name(self):
        try:
            return self.basic_data['DisplayName']['Localisation-cUserLocalisedString']['English']['#text']
        except KeyError:
            return

    @property
    def player_service(self):
        for consist in self.detailed_data['cConsist']:
            try:
                if consist['Driver']['cDriver']['PlayerDriver']['#text'] == '1':
                    return consist
            except (KeyError, TypeError):
                pass
        logging.error('Unable to fetch player service', json.dumps(self.detailed_data['cConsist'], indent=4))

    @property
    def route(self):
        return Route(self.route_xml)

    @property
    def service_name(self):
        try:
            return self.player_service['Driver']['cDriver']['ServiceName']['Localisation-cUserLocalisedString']['English']['#text']
        except TypeError:
            return ''

    @property
    def scenario_class(self):
        return self.basic_data['ScenarioClass']['#text']

    @property
    def start_datetime(self):
        start_seconds = int(float(self.basic_data['StartTime']['#text']))
        start_day = int(self.basic_data['StartDD']['#text'])
        start_month = int(self.basic_data['StartMM']['#text'])
        start_year = int(self.basic_data['StartYYYY']['#text'])

        if all([start_seconds, start_day, start_month, start_year]):
            try:
                start_date = datetime.datetime(start_year, start_month, start_day)
                start_date += datetime.timedelta(seconds=start_seconds)
                return start_date
            except ValueError:
                pass

    @property
    def start_location(self):
        try:
            return self.basic_data['StartLocation']['Localisation-cUserLocalisedString']['English']['#text']
        except KeyError:
            return ''

    @property
    def uuids(self):
        return [
            e['#text'] for e in self.basic_data['ID']['cGUID']['UUID']['e']
        ]

    @property
    def vmax(self):
        try:
            vmax_kph = int(self.player_service['MaxPermissibleSpeed']['#text'])
            return round(vmax_kph / 1.609)
        except (KeyError, ValueError):
            return


def dictget(dikt, key):
    d = dikt
    for k in key.split('.'):
        d = d[k]
    return d


def die(message='', code=1):
    if message:
        print(message, file=sys.stderr)
    sys.exit(code)


def ensure_config_present(folder):
    config_path = os.path.join(folder, 'dispatcher.yaml')
    if not os.path.exists(config_path):
        with open(config_path, 'w') as f:
            f.write(TEMPLATE_CONFIG)
    return config_path


def entry_banner():
    print("""Welcome to  Railworks Dispatcher 0.4
    """)


def exit_banner():
    print("""
Right Away Driver
    """)


def ensure_folder(path):
    try:
        os.makedirs(path)
        return True
    except OSError:
        return False


def get_last_number(work_orders_folder):
    pattern = os.path.join(work_orders_folder, '????.html')
    all_htmls = sorted(glob.glob(pattern))
    if not all_htmls:
        return 0
    last_file = os.path.split(all_htmls[-1])[1]
    last_number = int(last_file.split('.')[0])
    return last_number


def get_steam_minutes_played(profile_id):
    steam_response = steam.api.interface('IPlayerService').GetRecentlyPlayedGames(steamid=profile_id)
    if not dictget(steam_response, 'response.total_count'):
        return 0
    for game in dictget(steam_response, 'response.games'):
        if game['appid'] == 24010:
            return game['playtime_2weeks']
    return 0


def get_steam_profile_id(nickname):
    steam_response = steam.api.interface('ISteamUser').ResolveVanityURL(vanityurl='centralniak')
    return dictget(steam_response, 'response.steamid')


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
    parser.add_argument('work_orders', nargs='?')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--list', action='store_true')
    return parser.parse_args(args)


def to_minutes(time_string):
    pattern = re.compile('(?P<inte>[0-9\.]{1,4})(?P<stri>[hm]{1})')
    try:
        i, s = pattern.match(time_string).groups()
        minutes = float(i) * 60 if s == 'h' else i
        return int(minutes)
    except AttributeError:
        raise ValueError('Value %s does not meet the expected format.' % time_string)


def _main():

    complete_orders = []
    """
    Work orders generated
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

    ignored_scenarios = None
    """
    A list of devstrings of disappointing scenarios that should be avoided
    """

    entry_banner()

    args = parse_args(sys.argv[1:])

    railworks_folder = os.getcwd()

    logfile = os.path.join(railworks_folder, 'dispatcher.log')
    loglevel = logging.DEBUG if args.debug else logging.ERROR
    logging.basicConfig(
        filename=logfile, format='\n%(asctime)-15s %(levelname)-8s %(message)s', level=loglevel
    )

    configfile = ensure_config_present(railworks_folder)
    config = yaml.load(open(configfile))
    logging.debug('Loaded config: %s' % config)

    ignored_scenarios = config['ignored_scenarios'] or []

    scenario_folders = os.path.join(railworks_folder,
                                    'Content', 'Routes', '*', 'Scenarios', '*', 'ScenarioProperties.xml')
    work_orders_folder = os.path.join(railworks_folder, 'WorkOrders')
    ensure_folder(work_orders_folder)

    dispatcher_folder = os.path.abspath(os.path.dirname(__file__))
    dispatcher_data_folder = os.path.join(dispatcher_folder, 'Dispatcher')
    dispatcher_artwork_folder = os.path.join(dispatcher_data_folder, 'Artwork')

    all_scenarios = glob.glob(scenario_folders)
    random.shuffle(all_scenarios)

    steam.api.key.set(STEAM_API_KEY)

    if not all_scenarios:
        die('No scenarios found. Are you sure you are running dispatcher from the correct folder?')

    if args.list:
        args.work_orders = len(all_scenarios)

    if args.work_orders is None:
        steam_minutes_less = None

        try:
            steam_config = dictget(config, 'steam')
            steam_profile = steam_config['profile']
            steam_hours_planned = steam_config['hours_two_weeks']

            assert steam_profile and steam_hours_planned

            if isinstance(steam_profile, str) and not steam_profile.isnumeric():
                steam_profile = get_steam_profile_id(steam_profile)

            steam_minutes_played = get_steam_minutes_played(steam_profile)
            steam_minutes_less = steam_hours_planned * 60 - steam_minutes_played

        except Exception as exc:
            logging.warning('Unable to fetch data from steam %s' % exc)

        else:
            logging.debug('Steam profile %s played %d minutes out of %d in last 2 weeks' %
                          (steam_profile, steam_minutes_played, steam_hours_planned * 60))
            print('According to Steam you played roughly %d hour(s) in the last two weeks.' % (steam_minutes_played / 60))
            print('That\'s %d minutes less than the planned %d hours.' % (steam_minutes_less, steam_hours_planned))
            print('You can just hit <Enter> to create the missing work orders.\n')

        print('How many work orders should I create?\n')
        print('* use a natural number such as 1 to create one working order')
        print('* use a phrase such as 30m or 2h to create scenario(s) that will last approximately that long \n')

        default = str(steam_minutes_less) + 'm' if steam_minutes_less is not None else '1'
        args.work_orders = input('... [default: %s] ' % default) or default

    try:
        order_minutes = to_minutes(args.work_orders)
        # if we set min duration to 1 minute, orders with incorrectly set duration of 0 will be left out
        needed_order_duration_span = (max(order_minutes - LOW_TOLERANCE, 1), order_minutes + HIGH_TOLERANCE)
        logging.debug('Required %d minutes. Will generate between %d and %d' % (order_minutes, needed_order_duration_span[0], needed_order_duration_span[1]))

    except (TypeError, ValueError):
        needed_order_count = int(args.work_orders)
        logging.debug('Required %d work orders')

    def should_continue(completed_list, duration):
        if needed_order_count is not None:
            return len(completed_list) < needed_order_count
        else:
            return not(needed_order_duration_span[0] < duration < needed_order_duration_span[1])

    logging.debug('Will create scenarios with following constraints: %s' % {
        'needed_order_count': needed_order_count,
        'needed_order_duration_span': needed_order_duration_span
    })

    while all_scenarios and should_continue(complete_orders, complete_order_duration):

        todays_work_order = all_scenarios[-1]
        all_scenarios.pop()

        # only allow scenarios from existing unpacked routes
        scenario_folder_suffix = os.path.join(*todays_work_order.split(os.sep)[-3:])
        route_folder = todays_work_order.replace(scenario_folder_suffix, '')
        route_description = os.path.join(route_folder, 'RouteProperties.xml')
        if not os.path.exists(route_description):
            continue

        # check if Scenario.bin was already unpacked to Scenario.xml
        todays_work_order_details = todays_work_order.replace('ScenarioProperties.xml', 'Scenario.xml')
        if not os.path.isfile(todays_work_order_details):
            todays_work_order_bin = todays_work_order_details.replace('.xml', '.bin')
            subprocess.check_output('.\Serz.exe %s' % todays_work_order_bin.replace(railworks_folder, '').strip(os.sep))

        try:
            scenario = Scenario(todays_work_order, todays_work_order_details, route_description)
        except Exception:
            continue

        if scenario.route.name in IGNORED_ROUTES:
            continue

        if scenario.scenario_class in IGNORED_SCENARIO_CLASSES:
            continue

        if scenario.devstring in ignored_scenarios:
            logging.debug('Skipping scenario {} because scenario ignored'.format(scenario))
            continue

        if (needed_order_duration_span is not None and
            complete_order_duration + scenario.duration > needed_order_duration_span[1]):
            continue

        if not scenario.name:
            continue

        complete_orders.append(scenario)
        complete_order_duration += int(scenario.duration) + BREAK_LENGTH

    if not complete_orders:
        die('Not able to generate any scenario meeting your requirements. Sorry.')

    # Output html only if not list mode
    if not args.list:
        last_work_order_number = str(get_last_number(work_orders_folder) + len(complete_orders)).zfill(4)

        template = os.path.join(dispatcher_data_folder, 'Templates', 'disposition.html')
        html = jinja2.Template(open(template).read()).render(
            artwork_folder=dispatcher_artwork_folder,
            orders=complete_orders
        )

        html_name = last_work_order_number + '.html'
        html_path = os.path.join(work_orders_folder, html_name)
        open(html_path, 'w').write(html)
        launch_html(html_path)

    # In list mode output scenarios grouped by route name
    else:
        route_name_getter = lambda order: order.route.name
        sorted_orders = sorted(complete_orders, key=route_name_getter)
        grouped_orders = itertools.groupby(sorted_orders, key=route_name_getter)
        for route, orders in grouped_orders:
            print('\n * %s: \n' % route)
            for order_context in orders:
                print('   * %s' % order_context['scenario_name'])
            input('')

    exit_banner()


def main():
    try:
        _main()
    except Exception as exc:
        sys.stdout.write('%s encountered in main loop. Please see dispatcher.log for details.\n' % type(exc).__name__)
        logging.exception('Exception encountered in main loop')


if __name__ == '__main__':
    main()
