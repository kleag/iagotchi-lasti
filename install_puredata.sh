#!/bin/bash

if [ -d "puredata/console" -a -d "puredata/IAGO_SOUND_PD" -a -d "puredata/pure-data" ] 
then
    echo "Puredata is already installed."
else
    if [ -f "puredata/puredata.tar.gz" ] 
    then
#         mkdir -p puredata/puredata
        cd puredata
        tar zxvf puredata.tar.gz
    fi
fi
