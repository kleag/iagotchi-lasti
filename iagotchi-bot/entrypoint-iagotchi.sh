#!/bin/bash

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



echo "entrypoint..."
exec_var=$( cat data/config.json | jq -r '.what_run' )

echo $exec_var

fetchstatus() {
  curl "http://127.0.0.1:8088"
}

 case $exec_var in "bot")
      cd ChatScript/BINARIES/
      ./LinuxChatScript64 &
      cd ../../
      python3 test_chatscript.py & python3 main.py 
     ;;
     "text")
      cd ChatScript/BINARIES/
      ./LinuxChatScript64 &
      cd ../../
      python3 test_chatscript.py & python3 main.py 
     ;;
     "similarity-with-topics")
     python3 similarity.py --topics y
     ;;
     "similarity-without-topics")
     python3 similarity.py --topics n
     ;;*)
     echo "You have failed to specify what to do correctly in data/config.json."
     exit 1
     ;;
 esac

