#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 15:46:57 2019

@author: frejus
"""

import datetime, subprocess, os, sys
from time import gmtime, strftime
if os.name == 'nt':
    # Microsoft TTS
    import win32com.client as wincl
    import pythoncom
    # For maryTTS
    import winsound

print('synthese module init')
class Synthese(object):
    
    def __init__(self, synthesize=False):
        self.synthesize = synthesize
    

    def synthese(self, resp):
            """
            Convert text to voice
            Available voices (can be modify in server_parameters file): pierre (male), jessica (female), default (female)
            """
            if self.synthesize:
                synthfile = 'synth-{}.wav'.format(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
                synthfile_ = 'static/assets/{}'.format(synthfile)

                if os.name == 'posix':
                    # Using pico2wave, Linux only
                    print('OS is {}. Speaking with pico2wave.'.format(os.name))
                    resp_synthese = ['pico2wave', '-l', 'fr-FR', '-w', synthfile_, resp,]
                    lecture = ['aplay', synthfile_]
                    subprocess.call(resp_synthese)
                    subprocess.call(lecture)
                elif os.name == 'nt':
                    # Using Microsoft Windows speach
                    print('OS is {}. Speaking with MS voice API.'.format(os.name))
                    try:
                        speak = wincl.Dispatch("SAPI.SpVoice")
                        speak.Speak(resp)
                        sys.stdout.flush()
                    except:
                        print('Unsupported os {}. No speech synthesis is available.'
                            .format(os.name))
                        
                return "{}:/{}".format(resp, synthfile_)
            else:
                   
                return resp
#                        
