#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  7 13:12:42 2018

@author: frejus
"""

import socket
from pathlib import Path
import pickle, os, subprocess, sys
import chatscript_settings
import datetime
from log import Log



class ChatscriptInstance(object):
    
    def __init__(self, lima=None, server="127.0.0.1", botname='iagotchi'):
        self.server = server
        self.start_time = None
        chatscript_settings.init()
        self.ports = chatscript_settings.ports
        self.botname = botname
        self.status = None
        self.botresponses = {            
				'iagotchi' : ("make test", "iagotchi ready"),
				'iagotchig5' : ("make test", "iagotchi ready"),
			}
        chatscript_settings.init()
        self.lima = lima
        print("Chatscript starting....")
        self.runChatscript()
        
        self.log = None
        
        
    def runChatscript(self):
        self.start_chatscript_processes()
        #cs = ChatscriptInstance()
        for bot, port in self.ports.items():
            if bot == self.botname:
                print('ChatscriptInstance compile {}'.format(bot))
                self.sendAndReceiveChatScript(text=":build {}".format(bot), 
                                            user="User", 
                                            bot="{}".format(bot))
                self.sendAndReceiveChatScript(text=":reset {}".format(bot),
										  user = 'User',
										  bot=bot)
            

    def runBot(self):
        self.status = None
        #print(self.botname)
        for bot, port in self.ports.items():
            #print(self.ports.items())
            if bot == self.botname:
                #print(bot)
                resp = self.sendAndReceiveChatScript(text=self.botresponses[bot][0],
										  user = 'User',
										  bot=bot)
                print(resp)
                if resp and self.botresponses[bot][1].lower() in resp.strip().lower():
                    self.status = "OK"
                    self.sendAndReceiveChatScript(text=":reset {}".format(bot),
										  user = 'User',
										  bot=bot)
        if self.status is None:
            sys.exit("[Iagotchi-Bot Error] Problem with ChatScript")
            
        
    
        
    def start_chatscript_processes(self):
        """
        Function to start the chatscript server in background.
        It checks first if the name of the bot is correct otherwise it starts on 'iagotchi' by default.
        """
        check_botname = False
        _port = None
        for bot, port in chatscript_settings.ports.items():
            if bot == self.botname:
                check_botname = True
                _port = port
                break
        if not check_botname:
            self.botname = "iagotchi"
            _port = chatscript_settings.ports[self.botname]
        
        print('start_chatscript_processes {}: {}>{} port={}'.format(self.botname,
                    chatscript_settings.chatscript_path,
                    chatscript_settings.chatscript_binary,
                    port))
        if os.name == 'nt':
            subprocess.Popen([chatscript_settings.chatscript_binary, 
                            'port={}'.format(_port), 'buffer=15*50'],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            cwd=chatscript_settings.chatscript_path,
                            shell=True)
        else:
            print("start_chatscript_processes run chatscript server on Linux")
            subprocess.Popen([chatscript_settings.chatscript_binary, 
                            'port={}'.format(_port)],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            cwd=chatscript_settings.chatscript_path)

    #TODO désactiver lima_processing
    def sendAndReceiveChatScript(self, text, user, bot, lima_processing=False, timeout=10):
        print('ChatscriptInstance.sendAndReceiveChatScript "{}", "{}", "{}" ; {}'
              .format(user, bot, text, self.ports[bot]))
        check_est_tu = False
        if "tu" in text or "-tu" in text:
            text = text.replace("tu", "toi")
        if "es-tu" in text or "es tu" in text:
            check_est_tu = True
        if text.strip().startswith('si'):
            text = text.replace('si', 'lorsque', 1)
        if not self.lima is None and lima_processing:
            text = self.lima.text_lima_tagger(text)
            print('sendAndReceiveChatScript.lima_processing.True: {}'.format(text))
            if "taire" in text and check_est_tu and "es-tu" not in text or not "es tu" in text:
                text = text.replace('taire', 'es tu')
        msg = u'%s\u0000%s\u0000%s\u0000' % (user+bot, bot, text)
        msgToSend = str.encode(msg)
        check_est_tu = False
#        print(msgToSend)
        try:
            # Connect, send, receive and close socket. Connections are not persistent
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)  # timeout in secs
            s.connect((self.server, self.ports[bot]))
            
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



    def start_iagotchi_bot(self):
        self.sendAndReceiveChatScript(text=":reset {}".format(self.botname), 
                                          user="User", 
                                          bot=self.botname)
        #self.start_time = datetime.datetime.now()
        #self.log = Log(self.start_time)
        return self.startup()
    
    def startup(self):
        self.start_time = datetime.datetime.now()
        self.log = Log(self.start_time, botname=self.botname)
        
        return self.log
        
 
