#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 2018

@author: Gael de Chalendar
"""

import os, json
#from lfs_Exceptions import chatscript_processus, findfile


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



