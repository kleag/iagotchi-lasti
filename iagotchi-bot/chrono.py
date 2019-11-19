"""
This script implements a timer that controls a session. 
It allows to stop a session or restart a conversation.
"""

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
        
        
    def run(self):
        print ("ChronoThread Starting ")
        while True:
            if self.status:
                print()
                while not self.externals.session_status == 'stop':
                    current_time = datetime.datetime.now()
                    if not self.current_response_time is None and not self.session_restart_duration is None :
                        duration = (current_time -  self.current_response_time).total_seconds()
                        if self.already_restarted > 0 and duration + self.already_restarted*self.session_restart_duration >= self.session_stop_duration:
                            self.chrono_process("sessionstop")
                            self.osc_client.sendOscAction('/iagotchi/session/stop')
                            self.externals.stop()
                            self.stop()
                            self.status = False
                            break
                        elif (current_time -  self.start_time).total_seconds() >= self.session_duration:
                            self.chrono_process("sessionstop")
                            
                            self.osc_client.sendOscAction('/iagotchi/session/stop')
                            self.externals.stop()
                            self.stop()
                            self.status = False
                            break
                        elif  duration >= self.session_restart_duration:
                            #print("stop stop stop stop")
                            self.chrono_process("code relance")
                            
                            self.current_response_time = datetime.datetime.now()
                            self.already_restarted += 1
                            #self.botresponse = rep
                    elif (current_time -  self.start_time).total_seconds() >= self.session_duration:
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
        print("thread run {}".format(response))
        rep = syn.synthese(response)
        self.log.save_in_file("-", response)

        if not self.botresponse_object is None:
            if 'synth-' in rep:
                rep = rep.split(':::')[0]
            self.botresponse_object.sendOsc('/iagotchi/botresponse','{}'.format(rep))
            if text == 'sessionstop':
                self.botresponse_object.sendOsc('/iagotchi/session/stop','{}'.format(datetime.datetime.now()))
        if self.osc_self_client  is not None:
            self.externals.stop_message = "sessionstop {}".format(rep)
            # ???? aucun script ne répond au message osc /sessionsstop
            # seul le serveur du script main.py repond à /sessionstop mais pas en osc en http ????
            self.osc_self_client.send('/sessionstop')
                    
    def sendAndReceiveChatScript(self, text, user, bot, server, port, timeout=0.5):
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
        self._stop.set() 
    def stopped(self): 
        return self._stop.isSet() 
