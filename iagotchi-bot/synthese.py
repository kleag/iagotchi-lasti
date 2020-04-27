#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 15:46:57 2019

@author: frejus
"""

import datetime, subprocess, os, sys
from time import gmtime, strftime
from pathlib import Path
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
        self.reading = False
        Path("/Dist/data/sounds").mkdir(parents=True, exist_ok=True)
    

    def synthese(self, resp, play_audio=False):
            """
            Convert text to voice
            Available voices (can be modify in server_parameters file): pierre (male), jessica (female), default (female)
            """
            if self.synthesize:
                synthfile = 'synth-{}.wav'.format(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
                synthfile_ = '/Dist/data/sounds/{}'.format(synthfile)
                soxfile = 'sox_{}'.format(synthfile)
                soxfile_ = '/Dist/data/sounds/{}'.format(soxfile)

                if os.name == 'posix':
                    # Using pico2wave, Linux only
                    self.reading = True
                    #print('OS is {}. Speaking with pico2wave.'.format(os.name))
                    resp_synthese = ['pico2wave', '-l', 'fr-FR', '-w', synthfile_, resp,]
                    conv_synthese = ['sox', synthfile_, '-r', '44100', soxfile_]
                    lecture = ['aplay', synthfile_]
                    subprocess.call(resp_synthese)
                    #print('SYNTHESIS {} > {}'.format(resp_synthese, synthfile_))
                    subprocess.call(conv_synthese)
                    #print('SAMPLE RATE CONV {} > {}'.format(conv_synthese, soxfile_))
                    if play_audio:
                        subprocess.call(lecture)
                    self.reading = False
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
                        
                return "{}:::{}".format(resp, soxfile)
            else:
                   
                return resp
#                        
