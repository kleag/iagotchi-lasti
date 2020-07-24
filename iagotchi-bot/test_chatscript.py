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

from chatscript import ChatscriptInstance
import argparse, json


with open(r'@CMAKE_INSTALL_PREFIX@/data/config.json', 'r') as sv:
    configfile = json.load(sv)

def main(botname):
    chatscript = ChatscriptInstance(botname=botname)
    chatscript.start_iagotchi_bot()
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--bot', help='bot name')
    
    bots = ['iagotchi', 'iagotchig5']
    
    args= parser.parse_args()
    
    if args.bot and args.bot.lower() in bots:
        main(bot=args.bot.lower())
    elif configfile and configfile['bot']['name'].lower() in bots:
        main(configfile['bot']['name'].lower())
        
