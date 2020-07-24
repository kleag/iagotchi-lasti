"""
This script implements a timer that controls a session. 
It allows to stop a session or restart a conversation.
"""

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

import threading, socket, datetime, json, sys
from synthese import Synthese
import osc

with open(r'@CMAKE_INSTALL_PREFIX@/data/config.json', 'r') as sv:
    configfile = json.load(sv)
try:
    syn = Synthese(configfile['synthesize'])
except:
    syn = Synthese()
class ChronoThread (threading.Thread):
    def __init__(self, log=None):
        threading.Thread.__init__(self)
        self._stop = threading.Event() 
        self.session_restart_duration = None
        self.session_stop_duration = None
        self.session_duration = None
        self.current_response_time = None
        if log is None:
            self.status = False
        else:
            self.status = True
        self.log = log
        self.botresponse_object = None
        self.already_restarted = 0
        self.session_need_to_stop = False
        self.server_object = None
        self.http_server_object = None
        self.start_time = None
        self.osc_client = osc.Client(host='0.0.0.0', port=9000)
        self.externals = None
        self.osc_self_client = None
        self.waiting_to_stop = False
        
        
    def run(self):
        print ("ChronoThread Starting ")
        while True:
            if self.status:
                print()
                while not self.externals.session_status == 'stop':
                    current_time = datetime.datetime.now()
                    #print(self.externals.user_is_speaking, self.externals.syn.reading)
                    if self.waiting_to_stop and not (self.externals.user_is_speaking or self.externals.syn.reading):
                        self.chrono_process("sessionend")
                        self.osc_client.sendOscAction('/iagotchi/session/stop')
                        self.externals.stop()
                        self.stop()
                        self.status = False
                        self.waiting_to_stop = False
                        break
                    if not self.current_response_time is None and not self.session_restart_duration is None :
                        duration = (current_time -  self.current_response_time).total_seconds()
                        if self.already_restarted > 0 and duration + self.already_restarted*self.session_restart_duration >= self.session_stop_duration:
                            if (self.externals.user_is_speaking or self.externals.syn.reading) and not self.waiting_to_stop:
                                self.waiting_to_stop = True
                            if not (self.externals.user_is_speaking or self.externals.syn.reading) and not self.waiting_to_stop:
                                self.chrono_process("sessionstop")
                                self.osc_client.sendOscAction('/iagotchi/session/stop')
                                self.externals.stop()
                                self.stop()
                                self.status = False
                                break
                        elif (current_time -  self.start_time).total_seconds() >= self.session_duration:
                            if (self.externals.user_is_speaking or self.externals.syn.reading) and not self.waiting_to_stop:
                                self.waiting_to_stop = True
                            if not (self.externals.user_is_speaking or self.externals.syn.reading) and not self.waiting_to_stop:
                                self.chrono_process("sessionstop")
                                self.osc_client.sendOscAction('/iagotchi/session/stop')
                                self.externals.stop()
                                self.stop()
                                self.status = False
                                break
                        elif  duration >= self.session_restart_duration:
                            #print("stop stop stop stop")
                            while self.externals.user_is_speaking or self.externals.syn.reading:
                                continue 
                            self.chrono_process("code relance")
                            
                            self.current_response_time = datetime.datetime.now()
                            self.already_restarted += 1
                            #self.botresponse = rep
                    elif (current_time -  self.start_time).total_seconds() >= self.session_duration:
                            if (self.externals.user_is_speaking or self.externals.syn.reading) and not self.waiting_to_stop:
                                self.waiting_to_stop = True
                            if not (self.externals.user_is_speaking or self.externals.syn.reading) and not self.waiting_to_stop:
                                self.chrono_process("sessionstop")
                                self.osc_client.sendOscAction('/iagotchi/session/stop')
                                self.externals.stop()
                                self.stop()
                                self.status = False
                                break
                            
                    
    def chrono_process(self, text):
        """
        Processing including different actions according to the evolution of session duration.
        Input: Text to send to Chatscript. 
        """
        response = self.sendAndReceiveChatScript(text, "User", self.externals.botname, "127.0.0.1", int(configfile['chatscript']['port']))
        response = self.externals.check_no_lima_option(response)
        #response = self.externals.postprocessing(response)
        if "lastoutput" in response.lower():
            response = self.externals.last_response
        rep = syn.synthese(response)
        print(">>>CHRONO>>> {}".format(rep))
        self.log.save_in_file("-", response)

        if not self.botresponse_object is None:
            if 'synth-' in rep:
                rep_ = rep.split(':::')[0]
            self.botresponse_object.sendOsc('/iagotchi/botresponse','{}'.format(rep_))
            self.botresponse_object.sendOsc('/iagotchi/synthfile','{}'.format(rep.split(':::')[1].replace('_stop_', '').replace('__hello__', '')))
            if text == 'sessionstop' or text == 'sessionend':
                self.botresponse_object.sendOsc('/iagotchi/session/stop','{}'.format(datetime.datetime.now()))
        if self.osc_self_client  is not None:
            if text == 'sessionstop':
                self.externals.stop_message = "sessionstop {}".format(rep)
                # ???? aucun script ne répond au message osc /sessionsstop
                # seul le serveur du script main.py repond à /sessionstop mais pas en osc en http ????
                self.osc_self_client.send('/sessionstop')
            elif 'code' in text:
                self.externals.relance = rep 
                self.osc_self_client.send('relance')
                    
    def sendAndReceiveChatScript(self, text, user, bot, server, port, timeout=10):
        print('ChronoThread.sendAndReceiveChatScript "{}", "{}", "{}" ; {}'
              .format(user, bot, text, int(port)))
        msg = u'%s\u0000%s\u0000%s\u0000' % (user+bot, bot, text)
        msgToSend = str.encode(msg)
#        print(msgToSend)
        try:
            # Connect, send, receive and close socket. Connections are not persistent
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)  # timeout in secs
            s.connect((server, port))
            print(msgToSend)
            s.sendall(msgToSend)
            msg = ''
            while True:
                chunk = s.recv(1024)
                if chunk == b'':
                    break
                msg = msg + chunk.decode("utf-8")
            s.close()
            print('msg {}'.format(msg))
            return msg
        except:
            return None

            
            
    def stop(self):
        #self._stop.set() 
        self.status = False
    def stopped(self): 
        return self._stop.isSet() 
