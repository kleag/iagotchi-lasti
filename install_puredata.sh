#!/bin/bash

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
# while true; do
#     read -p "Do you wish to add docker this program?" yn
#     case $yn in
#         [Yy]* ) make install; break;;
#         [Nn]* ) exit;;
#         * ) echo "Please answer yes or no.";;
#     esac
# done
