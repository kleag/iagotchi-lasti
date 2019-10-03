#!/bin/bash

exec_var=$( cat data/config.json | jq -r '.what_run' )

echo $exec_var

 case $exec_var in "bot")
      cd ChatScript/BINARIES/
      ./LinuxChatScript64 &
      cd ../../
      python3 test_chatscript.py & python3 main.py
     ;;
     "similarity")
     python3 similarity.py
     ;;
     "similarité")
      python3 similarity.py
     ;;
     *)
     echo "You have failed to specify what to do correctly in data/config.json."
     exit 1
     ;;
 esac

