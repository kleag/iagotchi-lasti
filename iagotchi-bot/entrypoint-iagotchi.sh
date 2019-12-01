#!/bin/bash

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
#       until $(curl --output /dev/null --silent --head --fail http://127.0.0.1:8088); do
#         sleep 2
#       done
#       echo ready
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

