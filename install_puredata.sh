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


apt-get update  # To get the latest package lists
apt-get install puredata -y
apt-get install pd-cyclone -y
apt-get install docker.io -y
apt-get install docker-compose -y

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

# add docker group
groupadd docker
gpasswd -a $USER docker
service docker restart
usermod -a -G docker $USER 

