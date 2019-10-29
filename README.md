

# Installation

* [Building from source code](#building-from-source-code) *(must to be updated)*
* [Docker container ](#docker-container)



# Building from source code 



## Build dependences

* Tools: cmake, ninja, libttspico-utils, c++, nltk, python3, sox, liblo

### Under Ubuntu, most of these dependencies are installed with the following packages:

```
$ sudo apt-get install -y build-essential ca-certificates gcc curl wget unzip git apt-utils \
libpq-dev  mercurial pkg-config python3 python3-dev python3-pip libttspico-utils alsa-utils \
sox git cmake cmake-data python-nltk libsox-fmt-all locales ninja-build pyliblo-utils make
```

### To install all python packages in an environment, follow these instructions.

After installing virtualenv, do:

```
$ mkvirtualenv --python=/usr/bin/python3 env_name
$ workon env_name
```

### Pyblio is installed with the following instructions:

```
wget http://downloads.sourceforge.net/liblo/liblo-0.29.tar.gz
tar xzf liblo-0.29.tar.gz && cd liblo-0.29
./configure
make install
cd .. && rm -R liblo*
pip3 install pyliblo 
```
### Installation of the python version of sent2vec:

```
$ git clone https://github.com/jbcdnr/sent2vec.git
$ cd sent2vec
$ make
$ pip3 install cython numpy nltk
$ pip3 install .
$ cd ..

```

### Installation of nltk stopwords data

```
$ python3 -m nltk.downloader -d nltk_data stopwords
```

## Lima docker

```
$ sudo docker  pull aymara/lima:latest
```

## Install Iagotchi Bot 

* Download the Iagotchi-bot folder and move it to an installation location. Let's suppose *install_folder*
the installation folder containing iagotchi-bot. Then follow the following instructions:

    ```
    >  cd install_folder
    >  mkdir Dist
    >  mkdir Build
    >  git clone https://github.com/ChatScript/ChatScript.git
    >  sudo chmod 755 ./ChatScript/BINARIES/LinuxChatScript64
    >  mv ChatScript Dist
    ```

* Define the following environment variable:

    ```
    IAGOTCHICHATSCRIPTINSTALLDIR=/path/to/install_folder/Dist/ChatScript
    ```

* Continue with the following instructions:

    ```
    >  cd Build
    >  cmake -DCMAKE_INSTALL_PREFIX=/path/to/install_folder/Dist ../iagotchi-bot -G Ninja
    >  ninja install 
    >  cd ../Dist
    >  mkdir -p static/assets
    ```

## Usage

### Configuring Bot 

All the configurations needed to run Iagotchi-bot are in the config.json file located in */path/to/install_folder/Dist/data*.
The configuration file is read by the system at each restart and the parameters are reset. The fields necessary to fill in the file are:


* {`session`} : fill with the durations in second of session time, of the user relaunch, etc ...
* {`lima`} : set the appropriate values for the Lima server address (127.0.0.1) and port (8090)
* {`botresponse`} : specify the port on which the bot must return its response.
* {`synthesize`} : set to False for using an external speech synthesis from the response.
* {`musique`} : specify the port on which the bot must return the music request.

### Running Bot 

There are two possible tasks to perform with the main script. Among other things, the ability to rebuild the embeddings sentences of the 
similarity module with the `--build` option before running (with `--run`) the bot's dialog system. This option allows you to take into account the news 
sentences collected during the execution of the bot.

* Running Lima

    You must first run lima before running the bot. 

    ```
    $ sudo docker run -p 0.0.0.0:8090:8080/tcp -it aymara/lima limaserver
    ```

* For calculating sentence embeddings

    ```
    $ python3 main.py --build similarity
    ```
* For running the dialogue system.

    ```
    $ python3 main.py --run bot
    
    ```
    
    Then lauch a browser and go to the URL http://127.0.0.1:8088/


# Docker container
    



## Lima
```
- sudo docker pull aymara/lima:latest

- sudo docker tag aymara/lima limaserver:latest
```

## Build Iagotchi-Bot
```
1- Access to parent folder of iagotchi-bot

2- sudo docker-compose build
```
## Run Iagotchi-Bot
```
sudo docker-compose up
```

## Usage

### Configuring Bot 

All the configurations needed to run Iagotchi-bot are in the config.json file located in */path/to/install_folder/Dist/data*.
The configuration file is read by the system at each restart and the parameters are reset. The fields necessary to fill in the file are:


* {`what_run`} -  using to specify what to run:  bot (set to **bot**) or embeddings calculation (set to **similarity**) 
 * {`bot`} - using to specify what topic to use: for *rencontre* topic set the name to **iagotchi**  and **iagotchig5** for *G5* topic.
* {`session`} - fill with the durations in second of session time, of the user relaunch, etc ...
* {`botresponse`} - specify host ip address and port on which the bot must return its response.
* {`synthesize`} - set to False for using an external speech synthesis.
* {`musique`} - specify the port on which the bot must return the music request.

Modify the line 14 in docker-compose.yml  with the full path to the shared folder.

### Running Bot 

   * For running the dialogue system.

    ```
    $ sudo docker-compose up  -d 
    ```
    
    
    Then launch a browser and go to the URL http://127.0.0.1:8088/

  * For stopping the system
      ```
    $ sudo docker-compose stop
    ```  
    
  * For starting the system
      ```
    $ sudo docker-compose start
    ```
    
#### Troubleshoot
Containers must be started separately to identify the cause of an error caused by the command *docker-compose up* 

> I see `Problem with ChatScript`

This error usually occurs when the chatscript server has not started properly perhaps due to a missing file in the sources of chatscript or an error in the name of the bot to launch. 
The following commands can provide a trace of the error:

**1.**  First, run limaserver container
```
$ sudo docker-compose run -d limaserver
```

**2.** Then, run and access to iagotchi container
```
$ sudo docker-compose run --service-ports iagotchi bash
```
**3.** In iagotchi container
```
root@211c9bbd9a0f:/Dist# cd ChatScript/BINARIES/
root@211c9bbd9a0f:/Dist/ChatScript/BINARIES# ./LinuxChatScript64 local
```
**4.** After entering a username,
```
HARRY:  Welcome to ChatScript.
fr: > :build iagotchi
```
  if you do not get the  following message, it is likely that the server encountered an error that will be displayed.
```
IAGOTCHI:  Je n'ai pas compris. Peux-tu reformuler, s'il te pla�t? notrule
fr: > 
```
>  I see `iagotchi_1 exited with code 137 `

This error is commonly associated with Docker for Mac not having enough RAM allocated to it. **Error 137** in Docker denotes that the container was ‘KILL’ed by ‘oom-killer’ (Out of Memory). This happens when there isn’t enough memory in the container for running the process.

So it is an easy fix, go to the Docker Menu and select *Preferences*  then the *Advanced* tab and increase the Memory. You have to increase it to at least 
**4.0GB**.

> `To debug and trace the line that causes the container crash`

You must perform the following steps after those previously described in 1 and 2.

**3.** In iagotchi container
```
root@211c9bbd9a0f:/Dist# python3 test_chatscript.py
root@211c9bbd9a0f:/Dist# python3 main.py --chat iagotchi
```