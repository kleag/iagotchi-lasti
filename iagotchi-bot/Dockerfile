FROM ubuntu:18.04

MAINTAINER frejus.laleye@cea.fr

ENV DEBIAN_FRONTEND=noninteractive

#install packages 
RUN apt-get update \ 
    && apt-get upgrade -y \
    && apt-get install -y \
    build-essential \
    ca-certificates \
    gcc \
    curl \
    wget \
    unzip \
    git \
    apt-utils \
    libpq-dev \
    make \
    mercurial \
    pkg-config \
    python3 \
    python3-dev \
    python3-pip \
    ssh \
    libttspico-utils \
    sox \
    git \
    cmake \
    cmake-data \
    python-nltk \
    libsox-fmt-all \
    locales \
    ninja-build \
    && apt-get update \
    && apt-get autoremove \
    && apt-get clean 
    
RUN locale-gen en_US.UTF-8  
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8
RUN locale
    
RUN mkdir -p iagotchi-bot
RUN mkdir -p Build
RUN mkdir -p Dist

RUN git clone https://github.com/ChatScript/ChatScript.git \
    && chmod 755 ./ChatScript/BINARIES/LinuxChatScript64

RUN mv ./ChatScript ./Dist

#sent2vec
RUN git clone https://github.com/jbcdnr/sent2vec.git
WORKDIR ./sent2vec
RUN make
RUN pip3 install cython numpy nltk
RUN pip3 install .

#nltk
WORKDIR /
RUN python3 -m nltk.downloader -d nltk_data stopwords

RUN wget http://downloads.sourceforge.net/liblo/liblo-0.29.tar.gz && \
    tar xzf liblo-0.29.tar.gz && cd liblo-0.29 && \
    ./configure && \
    make install && \
    cd .. && rm -R liblo* && \
	pip3 install pyliblo 
	

RUN apt install -y pyliblo-utils alsa-utils nano net-tools inetutils-ping jq python3-requests



# RUN 

COPY requirements.txt ./
RUN pip3 install -r ./requirements.txt

COPY . /iagotchi-bot/




# Build
WORKDIR /Build 


ENV IAGOTCHICHATSCRIPTINSTALLDIR /Dist/ChatScript

RUN cmake  -DCMAKE_INSTALL_PREFIX=/Dist /iagotchi-bot -G Ninja
RUN ninja install


EXPOSE 8088
EXPOSE 1024
EXPOSE 5005
EXPOSE 5009
WORKDIR /Dist
RUN chmod +x entrypoint-iagotchi.sh
RUN pip3 install pathlib


RUN mv /nltk_data/ /usr/
RUN mkdir -p static/assets





CMD ["./entrypoint-iagotchi.sh", "-g", "daemon off;"]


