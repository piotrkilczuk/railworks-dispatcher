#!/usr/bin/env python

import os
import _winreg

import jinja2


steam_key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\\Valve\\Steam')
steam_path = _winreg.QueryValueEx(steam_key, 'SteamPath')[0]
railworks_path = os.path.join(steam_path, 'steamApps', 'common', 'railworks')
railworks_exe = os.path.join(railworks_path, 'railworks.exe')

if os.path.isfile(os.path.join(railworks_path, 'railworks.exe')):
	raw_input(os.path.abspath(railworks_exe))


