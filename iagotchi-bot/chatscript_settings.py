
# -*- coding: utf-8 -*-
"""
This script allows to specify the botnames and the ports 
to which the requests are sent.
"""
#
# Copyright 2020 CEA LIST
# This file is part of Iagotchi-bot.
# Iagotchi-bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# Iagotchi-bot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with Iagotchi-bot.  If not, see <http://www.gnu.org/licenses/>
# 
#

import os, json


with open(r'@CMAKE_INSTALL_PREFIX@/data/config.json', 'r') as sv:
    configfile = json.load(sv)
#server_file = settings.SERVERFILE
def init():
    global ports, chatscript_path, chatscript_binary, marytts_path, marytts_binary, lima_binary
    ports = {
        'iagotchi' : int(configfile['chatscript']['port']),
        'iagotchig5' : int(configfile['chatscript']['port']),
    }

    chatscript_path = r'{}'.format(os.path.join(os.path.join(os.getcwd(), 'ChatScript'),'BINARIES'))
    chatscript_binary = r'@CHATSCRIPT_BIN@'



