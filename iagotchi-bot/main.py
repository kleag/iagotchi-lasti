from __future__ import print_function
import bottle, osc, sys
from synthese import Synthese

from chatscript import ChatscriptInstance
from chatscript_externals import Externals
from bottle import static_file, route, template #, ServerAdapter, server_names
from socket import gethostname
import pickle, json, argparse
from similarity import sent2vecProcess
import os
#from iagotchiGUI import iagotchiGui
import threading
#import easygui



#gui = iagotchiGui()


        


with open(r'@CMAKE_INSTALL_PREFIX@/data/config.json', 'r') as sv:
    configfile = json.load(sv)
    
    
class CHAT(object):
    """
    To chat with text
    """
    def __init__(self, botname='iagotchi'):
        self.botname=botname
        self.externals = Externals(botname=self.botname)
        self.transcript = None
        self.botresponse = None
        
    def run(self):
        while True:
            if self.externals.poesie:
                reps = self.externals.poesie_generation()
                self.externals.poesie = False
            else:
                self.transcript = input("User :")
                reps = self.externals.run(self.transcript)
            print("Iagotchi : {}".format(reps))
        
        
    

class ASR(object):
    global is_restart_needed

    def __init__(self, osc_server_port=9000, osc_client_host='0.0.0.0', osc_client_port=9001, http_server_port=8088, botname='iagotchi'):
        self.ready = False
        self.osc_server_port = osc_server_port
        self.osc_client_host = osc_client_host
        self.osc_client_port = osc_client_port
        osc.setup(osc_client_host, osc_client_port)
        self.osc_self_client = osc.Client(osc_client_host, osc_server_port)
        self.botname=botname
        self.externals = Externals(botname=self.botname)
        try:
            self.osc_client = osc.Client(self.externals.botresponse_host, self.externals.botresponse_port)
            #self.osc_client_music = osc.Client(self.externals.music_host, self.externals.music_port)
        except:
            self.osc_client = None

        self.http_server_port = http_server_port
        self.silent = True
        self.sentence_num = 0
        self.is_restart_needed = True
        
        self.http_server = bottle.Bottle()

        #For CEA's modules
        self.transcript = None
        self.botresponse = None

        #END
        
        self.silent = False
        self.osc_server = osc.Server(host='0.0.0.0', port=self.osc_server_port, callback=self.osc_server_message)
        self.osc_server.run(non_blocking=True)
        self.ready = True
        print()
        print('*** Please open chrome at http://127.0.0.1:%d' % self.http_server_port)
        print()
        print("*********************************************************************")
        print('******       Please open chrome at http://127.0.0.1:%d       ******' % self.http_server_port)
        print("*********************************************************************")


        
        self._route()

        
    def _route(self):
        self.http_server.route('/', method="GET", callback=self.index)
        self.http_server.route('/result', method="POST", callback=self.result)
        self.http_server.route('/need_restart', method="GET", callback=self.need_restart)
        self.http_server.route('/sessionstop', method="GET", callback=self.sessionstop)
        self.http_server.route('/tmpResponse', method="GET", callback=self.tmpResponse)
        self.http_server.route('/relance', method="GET", callback=self.relance)
        self.http_server.route('/static/assets/<filename>', method="GET", callback=self.server_static)
        
        

    def osc_server_message(self, message, text=None):
        # print('OSC message = "%s"' % message)
        if message == '/record':
            self.silent = False
        elif message == '/pause':
            self.silent = True
        elif message == '/restart':
            # self.osc_server.shutdown()
            # os.execlp(sys.executable, sys.executable, *sys.argv)
            self.is_restart_needed = True
            self.silent = False
        elif message == '/exit':
            self.osc_server.shutdown()
            self.http_server.close()
            sys.exit(0)
        #elif message == '/botresponse':
            
        #elif message == '/synthese':

    def result(self):
        result = {'transcript': bottle.request.forms.getunicode('transcript'),
                'confidence': float(bottle.request.forms.get('confidence', 0)),
                'sentence': int(bottle.request.forms.sentence)}
        mess = ("   " + result['transcript'] + "   ").encode('utf-8') #.strip('<eos>')
        if self.silent == True:
            if result['sentence'] == 1:
                print("(pause)phrase  _" + mess)
                self.sentence_num += 1
            else:
                print("(pause)mots    _" + mess)
                self.externals.user_is_speaking = True
            return 'ok'
        if result['sentence'] == 1:
            print("phraseee  _" + mess.decode('utf8'))
            self.externals.user_is_speaking = False
            self.transcript = mess.decode('utf8')
            self.sentence_num += 1
            self.osc_client.sendOsc('/iagotchi/user','{}'.format(self.transcript))
            reps = self.externals.run(self.transcript, self.osc_client, self.osc_self_client)
            print('from reps {}'.format(reps))
            if reps and reps == "stop":
                return None
            if  reps and "_stop_" in reps:
                self.sendResponse(action='stop')
            if reps and "synth-" in reps:
                if self.osc_client:
                    self.sendResponse(action='result', text=reps.split(':::')[0], synthfile=reps.split(':::')[1].replace('_stop_', '').replace('__hello__', ''))
            #TODO implémebnter musique
            if reps and "start_music" in reps:
                reps = reps.replace('start_music', '')
                self.sendResponse(action='start_music')
            elif reps and "stop_music" in reps:
                reps = reps.replace('stop_music', '')
                self.sendResponse(action='stop_music')
            
            if self.osc_client and reps and "synth-" in reps:
                self.sendResponse(action='iagotchi', text=reps.split(':::')[0].replace('_stop_', '').replace('__hello__', ''))
            else:
                self.sendResponse(action='iagotchi', text=reps.replace('_stop_', '').replace('__hello__', ''), synthfile=reps.split(':::')[1].replace('_stop_', '').replace('__hello__', ''))
            if self.externals.poesie:
                #self.osc_self_client.send('/tmpResponse')
                self.sendResponse(action='poesie')
            return reps
        # ici pour renvoyer en osc la reconnaissance temporaire (sentence = 0)
        else:
            tmp = mess.decode('utf8')
            print("words     _" + tmp)
            self.osc_client.sendOsc('/iagotchi/user_tmp','{}'.format(tmp))
            return 'ok'

    def sendResponse(self, action, text=None, synthfile=None):
        print('sending of {}'.format(text))
        if action == 'stop':
            self.osc_client.sendOscAction('/iagotchi/session/stop')
        elif action   == 'start_music':
            self.osc_client.sendOscAction('/iagotchi/music/start')
        elif action ==  'stop_music':
            self.osc_client.sendOscAction('/iagotchi/music/stop')
        elif action == 'result':
            self.osc_client.sendOsc('/result/botresponse', text)
            self.osc_client.sendOsc('/result/synthfile', synthfile)
        elif action == 'iagotchi':
            self.osc_client.sendOsc('/iagotchi/botresponse', text)
            self.osc_client.sendOsc('/iagotchi/synthfile', synthfile)
        elif action == 'poesie':
            self.osc_self_client.send('/tmpResponse')
            
            

  
    def result_testfile(self, in_filename):
        with open(in_filename, 'r', encoding='utf8') as f:
            for line in f:
                line = line.strip()
                if line:
                    line = line.replace("#!", "")
                    reps = self.externals.run(line.strip(), self.osc_client)
                    with open('G5results_from_testfile.txt', 'a', encoding='utf8') as out:
                        out.write("{}::{}\n".format(line, reps))

    def need_restart(self):
        if self.is_restart_needed:
            self.is_restart_needed = False
            return 'yes'
        return 'no'
    def sessionstop(self):
        if self.externals.stop_message is not None:
            stpmsg = self.externals.stop_message.replace('sessionstop', '')
            self.externals.stop_message = None
            return stpmsg
    def tmpResponse(self):
        if self.externals.poesie:
            tmpmsg = self.externals.poesie_generation()
            self.externals.poesie = False
            self.osc_client.sendOsc('/iagotchi/botresponse','{}'.format(tmpmsg))
            #tmpmsg = self.externals.tmp_message
            #self.externals.tmp_message = None
            #self.externals.tmp_message_sent = True
            return tmpmsg
    def relance(self):
        tmprelance = self.externals.relance
        self.externals.relance = None
        return tmprelance
        
    
    def start(self):
        self.http_server.run(host='0.0.0.0', port=self.http_server_port, quiet=True, debug=True)
        #run_simple('0.0.0.0', self.http_server, ssl_context=context)
    
    
    #@route('/static/assets/<filename>')
    def server_static(self, filename):

        return static_file(filename, root='./static/assets')
    
    #@route('/')
    def index(self):
        return template('index')


class BuildSimilarityResponses(object):

    
    def __init__(self):
        self.data = dict()
        for topic in configfile['topic']['list']:
            if os.path.exists('data/{}.txt'.format(topic)):
                with open('data/{}.txt'.format(topic), 'r') as txtfile:
                    self.data[topic] = txtfile.readlines()
            else:
                sys.exit("[Iagotchi-Bot Error] {} doesn't exist.".format('data/{}.txt'.format(topic)))
        self.responses = None
        try:
            with open('data/responses.pkl', 'rb') as f:
                self.responses =  pickle.load(f)
        except:
            pass
                    
    
    def build_data(self):
        print('build response file')
        if not self.responses is None:
            for topic in configfile['topic']['list']:
                if os.path.exists('data/{}.txt'.format(topic)):
                     with open('data/{}.txt'.format(topic), 'r') as txtfile:
                         for i, line in enumerate(txtfile):
                             lst4line = self.responses[topic][i]
                             lst4line = list(dict.fromkeys(lst4line))
                             print('lst4line {}'.format(lst4line))
                             ind_ = [j for j, l in enumerate(lst4line) if "Je n'ai pas compris. Peux-tu reformuler" in l]
                             if len(ind_) > 0:
                                 lst4line.remove(lst4line[ind_[0]])
                             if len(lst4line) > 1:
                                 for text in lst4line:
                                     if not text.strip() == self.data[topic][i+1]:
                                         self.data.append(line)
                                         self.data.append(text)
        else:
            sys.exit("[Iagotchi-Bot Error] {} doesn't exist.".format('responses.pkl'))
            
    def save_data(self):
        print('save data')
        for topic, lines in self.data.items():
            os.remove('data/{}.txt'.format(topic))
            with open('data/{}.txt'.format(topic), 'a') as f_out:
                for line in lines:
                    f_out.write('{}\n'.format(line.strip()))
    def build_similarity(self):
        print('build data embeddings')
        sv = sent2vecProcess("data")
        sv.run()
        
                    
            
        
def showGui():
    gui.showGui()
    gui.exit()

from multiprocessing import Process

def run_cpu_tasks_in_parallel(tasks):
    running_tasks = [Process(target=task) for task in tasks]
    for running_task in running_tasks:
        running_task.start()
    for running_task in running_tasks:
        running_task.join()
        
def main_run():
    externals = Externals()
    syn = Synthese()
    asr = ASR()
        
    asr.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--build', help='build option: similarity or responses')
    parser.add_argument('--runbot', help='iagotchi or iagotchig5')
    parser.add_argument('--testfile', help='test questions in file')
    parser.add_argument('--chat', help='using text to chat')
    
    bots = ["iagotchi", "iagotchig5"]
    
    args= parser.parse_args()

    if args.build and args.build.lower() == 'similarity':
        bsr = BuildSimilarityResponses()
        bsr.build_data()
        bsr.save_data()
        bsr.build_similarity()         
    elif args.build and args.build.lower() == 'responses':
        print('build response file')
    elif args.runbot:
        print(configfile['bot']['name'])
        if args.runbot and  args.runbot.lower() in bots:
            asr = ASR(botname=args.runbot.lower())
            asr.start()
        elif configfile['bot']['name'] in bots:
            asr = ASR(botname=configfile['bot']['name'])
            asr.start()


    elif args.testfile and os.path.isfile(args.testfile):
        asr = ASR()
        asr.result_testfile(args.testfile)
        
    elif args.chat and args.chat.lower() in bots:
        cht = CHAT(botname=args.chat.lower())
        cht.run()
        
    elif configfile['bot']['name'].lower() in bots:
        print(configfile['bot']['name'])
        if args.runbot and  args.runbot.lower() in bots:
            asr = ASR(botname=args.runbot.lower())
            asr.start()
        elif configfile['bot']['name'] in bots:
            asr = ASR(botname=configfile['bot']['name'])
            asr.start()
        
        

        
        
        
        
