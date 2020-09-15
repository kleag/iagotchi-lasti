"""
This script is the core of the system. It contains the functions 
to retrieve the transcription, perform a pretreatment, 
send to the ChatScript engine, postprocess the response obtained 
and some other operations required by the dialogue system.
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

import re, json, datetime, sys
from chatscript import ChatscriptInstance
import threading
from synthese import Synthese
import socket
from chrono import ChronoThread
from lima import Lima
from similarity import Similarity
#import wikipedia
from generator.generator import Generator
import random, os
from nltk.corpus import stopwords
import pickle
from wiki import Wiki
from time import sleep
import netifaces


wikip = Wiki(language='fr')

 
all_raw_stopword = stopwords.words('french')
raw_stopword_top_list = all_raw_stopword[0:64]


with open(r'@CMAKE_INSTALL_PREFIX@/data/config.json', 'r') as sv:
    configfile = json.load(sv)
    

    
lstbonjour = ["allo", "allô", "aloha", "bon après-midi", "bonjour", "bonjour et bienvenue", "bonsoir", "c'est bien de vous revoir", "content de te rencontrer", "enchanté", "hella", "hello", "hey", "hey toi", "hiya", "salutations", "salut", "sympa de te rencontrer", "sympa de te voir", "coucou"]
stpwds = ['qu', 'que', 'qui', 'ne', 'pas', "n'"]
punctuations = '''!()[]{};:"\,<>./?@#$%^&*'''
RE_STRIP_REFS = re.compile("\.?\[\d+\]?")


for wd in stpwds:
    try:
        raw_stopword_top_list.remove(wd)
    except:
        continue

chrono = ChronoThread(log=None)
chrono.start()

def get_ip_default_route():
    if 'posix' in os.name:
        return netifaces.gateways()['default'][netifaces.AF_INET][0]
    else:
        return 'host.docker.internal'
class Externals(object):
    
    def __init__(self, botname='iagotchi'):
                
        self.need_user_name = False
        self.need_stop = False
        self.user_name = None
        self.session_stop_duration = int(configfile['session']['stop'])
        self.session_restart_duration = int(configfile['session']['restart'])
        self.last_response = None
        self.interaction_counter = 0
        self._transcript = None
        self.need_restart_postprocessing = False
        self.botname = botname
        # For Lima
        self.lima = Lima()
        #####
        print('Externals.init: similarity module loading ...')
        self.similarity = Similarity(using=configfile['similarity']['ToUse'], lima=self.lima)
        print('Externals.init: generator module loading ...')
        self.generator = Generator('generator/iagotchi.model')
        print('Externals.init: ChatscriptInstance loading ...')
        self.chatscript = ChatscriptInstance(lima=self.lima, botname=self.botname)
        
        print("##Run iagotchi bot")
        self.chatscript.runBot()
        self.log = None
        self.chrono = chrono
        self.session_status = None
        #self.startup()
        # Get the parameters related to the duration of a session
        try:
            self.chrono.session_restart_duration = int(configfile['session']['restart'])
            self.chrono.session_stop_duration = int(configfile['session']['stop'])
            self.chrono.session_duration = int(configfile['session']['duration'])
            if self.chrono.session_restart_duration > self.chrono.session_stop_duration:
                sys.exit("[Iagotchi-Bot Error] Value of stop field in session must not be less than restart value.")
        except:
            sys.exit("[Iagotchi-Bot Error] Stop, Restart and Duration values must be integers.")
        # End duration parameters getting
        
        self.definition = dict()
        self.themes = configfile['themes']
        self.themes_used = list()
        self.chatscriptkeywords = configfile["chatscript_keywords"]
        self.using_topic_responses = None #self.load_responses_pickle_obj()
        try:
            ip = get_ip_default_route()
            print(">>>>IP>>>> {}".format(ip))
            self.botresponse_host = get_ip_default_route()
            #self.botresponse_host = configfile['botresponse']['ip']
            self.botresponse_port = int(configfile['botresponse']['port'])
            #self.music_host = configfile['musique']['ip']
            #self.music_port = int(configfile['musique']['port'])
        except:
            pass
            #self.music_port = 5007
        self.start_music = None
        self.definitions_from_db = dict()
        self.stop_message = None
        self.no_use_lima = False
        self.osc_client = None
        self.osc_self_client = None
        self.tmp_message = None
        self.tmp_message_sent = False
        self.poesie = False
        self.relance = None
        self.log = self.chatscript.start_iagotchi_bot()
        self.chrono.log = self.log
        if len(self.themes) > 0:
            for th in self.themes:
                res = self.log.getDefinition(th)
                if not res is None:
                    self.definitions_from_db[th] = res
        self.user_is_speaking = False
        try:
            self.syn = Synthese(configfile['synthesize'])
        except:
            self.syn = Synthese()
            
        
    def startup(self):
        print('startup at {}'.format(datetime.datetime.now()))
        self.log = self.chatscript.start_iagotchi_bot()
        self.chrono.log = self.log
          
        
        self.chrono.start_time = self.chatscript.start_time
        self.chrono.current_response_time = None
        self.chrono.externals = self
        
        self.session_status = 'start'
        self.chrono.status = True
        self.need_stop = False
        self.stop_message = None
        self.tmp_message = None
        self.relance = None
        
        
        self.user_name = None
        self.osc_self_client = None
        self.tmp_message_sent = False
        self.poesie = False
        if self.osc_client is not None:
            self.osc_client.sendOsc('/iagotchi/session/start','{}'.format(self.chrono.start_time))
        self.user_is_speaking = False
        self.input_mode = None
        self.Output_mode = None
        try:
            self.syn = Synthese(configfile['synthesize'])
        except:
            self.syn = Synthese()
        print('End startup at {}'.format(datetime.datetime.now()))
        
    
    
    def postprocessing(self, response):
        #response = response.lower()
        print("externals.postprocessing response {} need_user_name: {} user_name: {}".format(response, self.need_user_name, self.user_name))
        print("externals.postprocessing: theme already discussed {}".format(len(self.themes_used)))
        if "sessionstart" in response.lower() and not self.need_user_name:
            self.need_user_name = True
            response = re.sub('sessionstart', ' ', response.lower())
        elif "sessionstart" in response.lower() and self.need_user_name:
            response = re.sub('sessionstart', ' ', response.lower())
            self.need_user_name = False
        elif "lastoutput" in response.lower():
            response = self.last_response
            
        elif "sessionstop" in response.lower():
            response = re.sub('sessionstop', ' ', response.lower())
            self.need_stop = True
        elif "notrule" in response.lower():
            """
            Recherche de question similaire; Recherche de règles pour la question similaire; Si réponse, renvoie réponse
            Sinon renvoie réponse renvoyée pour module de recherche de questions similaires. 
            """
            response_ = re.sub('notrule', ' ', response.lower())
            print('chatscript_externals.postprocessing: response--> {} need to search similar question'.format(response_))
            #distance, qid,  transcript_similar, repsimilar = self.similarity.tfidf_simlarity(self._transcript)
            distance, qid,  transcript_similar, repsimilar = self._get_similarity(self._transcript, 'rencontre')
            print('chatscript_externals.postprocessing similar question found: {}'.format(transcript_similar))
            #response = repsimilar
            response = self.chatscript.sendAndReceiveChatScript(self.preprocessing(transcript_similar), "User", self.botname, lima_processing=True)
            if 'notrule' in response.lower() and repsimilar is None:
                response = re.sub('notrule', ' ', response.lower())
            elif 'notrule' in response.lower() and not repsimilar is None:
                response = repsimilar
            elif not 'notrule' in response.lower():
                self.need_restart_postprocessing = True
                
        elif "wikipedia4generalword" in response.lower():
            response_ = re.sub('wikipedia4generalword', '', response.lower())
            chk = [1 for item in self.themes if item == response_.strip().lower()]
            if not len(chk) > 0:
                response_ = self._NC_entity(response_)
            elif len(chk) > 0 and chk[0] == 1:
                response_ = [response_.strip()]
            print('postprocessing response_ {}'.format(response_))
            if not response_ is None:
                for i, elt in enumerate(response_):
                    if elt.lower() in self.definition.keys():
                        response = self.chatscript.sendAndReceiveChatScript("définition existe déjà  {} dans la base de données".format(elt.lower()), "User", self.botname)
                        response = '{} {}'.format(response, self.definition[elt.lower()])
                        response = response.split()
                        index_ = [response.index(keyword) for keyword in self.chatscriptkeywords if keyword in response]
                        if len(index_) > 0:
                            response = ' '.join(response[0:index_[0]])
                        else:
                            response = ' '.join(response)
                        break
                    # si le thème n'est pas encore abordé, définition connue et nombre de thèmes abordés < 3
                    elif elt.lower() in self.definitions_from_db.keys() and not elt.lower() in self.definition.keys() and len(self.themes_used) < 3:
                        if elt.lower() in self.themes:
                            self.log.theme_insertion(elt.lower(), definition)
                        definition = random.choice(self.definitions_from_db[elt.lower()])
                        self.definition[elt.lower()] = definition
                        response = definition
                        break
                    # si le thème n'est pas encore abordé, définition connue et nombre de thèmes abordés >= 3
                    elif elt.lower() in self.definitions_from_db.keys() and not elt.lower() in self.definition.keys() and len(self.themes_used) >= 3: 
                        response = self.chatscript.sendAndReceiveChatScript("relance question", "User", self.botname)
                        break
                        
                     # si le mot pas abordé, mot n'est pas un thème
                    elif not elt.lower() in self.definitions_from_db.keys() and not elt.lower() in self.definition.keys():
                        wiki_options = None
                        definition = None
                        definition, wiki_word, elt = wikip.run(elt.lower())

                        #try:
                            #definition = wikipedia.summary(elt.lower(), sentences=1)
                        #except wikipedia.exceptions.DisambiguationError as e:
                            #wiki_options = e.options
                        
                        if wiki_word is None and definition is not None: # si la def du mot est trouvée
                            try:
                                response = definition
                                self.definition[elt.lower()] = definition
                                if elt.lower() in self.themes:
                                    self.log.theme_insertion(elt.lower(), definition)
                                    self.themes_used.append(elt.lower())
                                break
                            except:
                                pass
                        elif wiki_word is not None and definition is not None:
                            try:
                                response = definition
                                self.definition[wiki_word.lower()] = definition
                                if wiki_word.lower() in self.themes:
                                    self.log.theme_insertion(wiki_word.lower(), definition)
                                    self.themes_used.append(wiki_word.lower())
                                break
                            except:
                                pass
                        elif definition is None and i < len(response_) - 1:
                            continue
                        elif definition is None:
                            response = self.chatscript.sendAndReceiveChatScript("def {}".format(elt.lower()), "User", self.botname)
                            self.need_restart_postprocessing = True
                            break

            else:
                response = self.chatscript.sendAndReceiveChatScript("relance question", "User", self.botname)
                response = "Pourquoi veux-tu parler de ça. {}".format(response)

                    
        elif "wikipediamocle0" in response.lower():
            """
            L'utilisateur ne connait pas la définition du thème. Le bot doit lui donner une définition.
            """
            print('chatscript_externals.postprocessing.wikipediamocle0 {}'.format(response))
            response_ = re.sub('wikipediamocle0', '', response.lower())
            mot = response_.split()[-1] # récupérer le thème de la réponse du Bot.
            print('postprocessing response_ {}'.format(response_))
            # si le thème est déjà abordé avec sa définition connue. 
            if mot.lower() in self.definition.keys():
                response = "{} {}".format(" ".join(response_.split()[0:-1]), self.definition[mot.lower()])
            # si le thème n'est pas encore abordé, définition connue et nombre de thèmes abordés < 3
            elif mot.lower() in self.definitions_from_db.keys() and not mot.lower() in self.definition.keys() and len(self.themes_used) < 3: 
                response = "{} {}".format(" ".join(response_.split()[0:-1]), random.choice(self.definitions_from_db[mot.lower()]))
                self.definition[mot.lower()] = random.choice(self.definitions_from_db[mot.lower()])
                self.themes_used.append(mot.lower())
            # si le thème n'est pas encore abordé, définition connue et nombre de thèmes abordés >= 3
            elif mot.lower() in self.definitions_from_db.keys() and not mot.lower() in self.definition.keys() and len(self.themes_used) >= 3: 
                response = self.chatscript.sendAndReceiveChatScript("relance question", "User", self.botname)
            # si le thème pas abordé, définition pas connue et nombre de thèmes abordés < 3
            elif not mot.lower() in self.definitions_from_db.keys() and not mot.lower() in self.definition.keys() and len(self.themes_used) < 3:
                definition = None
                definition, wiki_word, mot = wikip.run(mot.lower())
                if wiki_word is None and definition is not None: # si la def du mot est trouvée                    
                    response = definition
                    self.definition[mot.lower()] = definition
                    if mot.lower() in self.themes:
                        self.log.theme_insertion(mot.lower(), definition)
                        self.themes_used.append(mot.lower())
                elif wiki_word is not None and definition is not None:
                    response = definition
                    self.definition[wiki_word.lower()] = definition
                    if wiki_word.lower() in self.themes:
                        self.log.theme_insertion(wiki_word.lower(), definition)
                        self.themes_used.append(wiki_word.lower())
                elif definition is None:
                    theme_temporary = [t for t in self.themes if t not in self.definition.keys()]
                    theme_ = random.choice(theme_temporary)
                    self.themes.remove(theme_)
                    self.themes_used.append(mot.lower())
                    response = self.chatscript.sendAndReceiveChatScript("question {} pas".format(theme_), "User", self.botname)
                    response = response.split()
                    index_ = [response.index(keyword) for keyword in self.chatscriptkeywords if keyword in response]
                    if len(index_) > 0:
                        response = ' '.join(response[0:index_[0]]) 
                    else:
                        response = ' '.join(response)
            # si le thème pas abordé, définition pas connue et nombre de thèmes abordés >= 3
            elif not mot.lower() in self.definitions_from_db.keys() and not mot.lower() in self.definition.keys() and len(self.themes_used) >= 3:
                definition = None
                definition, wiki_word, mot = wikip.run(mot.lower())
                if wiki_word is None and definition is not None: # si la def du mot est trouvée  
                    response = definition
                    self.definition[mot.lower()] = definition
                    if mot.lower() in self.themes:
                        self.log.theme_insertion(mot.lower(), definition)
                elif wiki_word is not None and definition is not None:
                    response = definition
                    self.definition[wiki_word.lower()] = definition
                    if wiki_word.lower() in self.themes:
                        self.log.theme_insertion(wiki_word.lower(), definition)
                elif definition is None:
                    response = self.chatscript.sendAndReceiveChatScript("relance question", "User", self.botname)


        elif "wikipediamocle1" in response.lower():
            """
            L'utilisateur donne une définition. Le bot doit l'enregistrer.
            """
            print('chatscript_externals.postprocessing.wikipediamocle1 {}'.format(response))
            response_ = re.sub('wikipediamocle1', '', response.lower())
            mot = response_.split()[-1]
            print('postprocessing response_ {}'.format(response_))
            # si le thème est déjà abordé avec sa définition connue. 
            if mot.lower() in self.definition.keys():
                response = "{} {}".format(" ".join(response_.split()[0:-1]), self.definition[mot.lower()])
            # si le thème n'est pas encore abordé, définition connue et nombre de thèmes abordés < 3
            elif mot.lower() in self.definitions_from_db.keys() and not mot.lower() in self.definition.keys() and len(self.themes_used) < 3:
                response = "{} {}".format(" ".join(response_.split()[0:-1]), random.choice(self.definitions_from_db[mot.lower()]))
                self.log.theme_insertion(mot.lower(), self._transcript)
                self.definition[mot.lower()] = random.choice(self.definitions_from_db[mot.lower()])
                self.themes_used.append(mot.lower())
            # si le thème n'est pas encore abordé, définition connue et nombre de thèmes abordés >= 3
            elif mot.lower() in self.definitions_from_db.keys() and not mot.lower() in self.definition.keys() and len(self.themes_used) >= 3: 
                response = self.chatscript.sendAndReceiveChatScript("relance question", "User", self.botname)
            # si le thème pas abordé, définition pas connue et nombre de thèmes abordés < 3
            elif not mot.lower() in self.definitions_from_db.keys() and not mot.lower() in self.definition.keys() and len(self.themes_used) < 3:
                try:
                    self.log.theme_insertion(mot.lower(), self._transcript)
                    self.definition[mot.lower()] = random.choice(self.definitions_from_db[mot.lower()])
                    self.definitions_from_db[mot.lower()] = [self._transcript]
                    self.themes_used.append(mot.lower())
                except:
                    pass
                response = self.chatscript.sendAndReceiveChatScript("relance question", "User", self.botname)
                response = "Ah oui? je vais rajouter ta réponse à ma base de donnée. {}".format(response)
            # si le thème pas abordé, définition pas connue et nombre de thèmes abordés >= 3
            elif not mot.lower() in self.definitions_from_db.keys() and not mot.lower() in self.definition.keys() and len(self.themes_used) >= 3:
                definition = None
                definition, wiki_word, mot = wikip.run(mot.lower())
                if wiki_word is None and definition is not None: # si la def du mot est trouvée  
                    response = definition
                    self.definition[mot.lower()] = definition
                    if mot.lower() in self.themes:
                        self.log.theme_insertion(mot.lower(), definition)
                elif wiki_word is not None and definition is not None:
                    response = definition
                    self.definition[wiki_word.lower()] = definition
                    if wiki_word.lower() in self.themes:
                        self.log.theme_insertion(wiki_word.lower(), definition)
                elif definition is None:
                    response = self.chatscript.sendAndReceiveChatScript("relance question", "User", self.botname)
                #response = self.chatscript.sendAndReceiveChatScript("relance question", "User", "iagotchi")
                
                    
        elif "wikipediamotcleinitial" in response.lower():
            response_ = re.sub('wikipediamotcleinitial', '', response.lower())
            response_ = self.check_no_lima_option(response_)
            mot = response_.split()[-1].lower()
            print('postprocessing response_ {}'.format(response_))
            if mot.lower() in self.definition.keys():
                response = self.chatscript.sendAndReceiveChatScript("définition existe déjà  {} dans la base de données".format(mot), "User", self.botname)
                response = '{} {}'.format(response, self.definition[mot])
                response = response.split()
                index_ = [response.index(keyword) for keyword in self.chatscriptkeywords if keyword in response]
                if len(index_) > 0:
                    response = ' '.join(response[0:index_[0]])
                else:
                    response = ' '.join(response)
            elif len(self.themes_used) >= 3:
                response = self.chatscript.sendAndReceiveChatScript("relance question", "User", self.botname)
            elif not mot in self.definitions_from_db.keys():
                definition = None
                definition, wiki_word, mot = wikip.run(mot.lower())
                if wiki_word is None and definition is not None: # si la def du mot est trouvée  
                    print('wikipedia definition of {} is {}'.format(mot, definition))
                    self.definitions_from_db[mot] = [definition]
                elif wiki_word is not None and definition is not None:
                    print('wikipedia definition of {} is {}'.format(wiki_word, definition))
                    self.definitions_from_db[wiki_word] = [definition]
                    
                response = response_.split()[0:-1]
                response = " ".join(response)

                
                
        elif "question4poesie" in response.lower():
            response_ = re.sub('question4poesie', 'Un instant', response.lower())
            response = self.check_no_lima_option(response_)
            try:
                self.osc_client.sendOsc('/iagotchi/botresponse','{}'.format(response))   
            except:
                pass
            self.poesie = True
            
            
                
        elif "qrelanceno" in response.lower():
            """
            Renvoie la réponse à une question similaire à celle de l'utilisateur. 
            """
            distance, qid,  transcript_similar, repsimilar = self._get_similarity(self.last_response, 'rencontre')
            print('chatscript_externals.postprocessing similar response found: {}'.format(repsimilar))
            response = repsimilar
            
        elif "qrelanceget" in response.lower():
            """
            Recherche une question similaire à celle de l'utilisateur si pas de règles.
            """
            response = response.replace('qrelanceget', '')
            response = self.chatscript.sendAndReceiveChatScript("{}".format(response), "User", self.botname, lima_processing=True)
            if 'notrule' in response:
                distance, qid,  transcript_similar, repsimilar = self._get_similarity(self.last_response, 'rencontre')
                print('chatscript_externals.postprocessing similar question found: {}'.format(transcript_similar))
                #self._save_response_in_file(response.replace('notrule', ''), 'rencontre', qid)
                response = repsimilar      
            else:
                self.need_restart_postprocessing = True
        elif '**lancermusique' in response.lower():
            """
            Le bot a détecter le mot musique. Pour envoyer /music au port configuré dans config.json, on passe la variable self.start_music à True
            """
            response = response.replace('**lancermusique', '')
            self.start_music = True
            
        elif '**stopmusique' in response.lower():
            """
            Le bot a détecter stop pendant que la musique est en cours de lecture. Pour envoyer /stop au port configuré dans config.json, on passe 
            la variable self.start_music à False
            """
            response = response.lower().replace('**stopmusique', '')
            self.start_music = False
            
                   
        response = self.check_no_lima_option(response)
        print("externals.postprocessing after response {} need_user_name: {} user_name: {}".format(response, self.need_user_name, self.user_name))
        self.last_response = response
        return response
    
    def poesie_generation(self):
        result = " "
        try:
            result = self.generator.generate(200)
            result = re.sub('<eos>', '.', ' '.join(result))
            r = True
            while r:
                if '. .' in result:
                    result = result.replace('. .', '.')
                else:
                    r = False
            result = "{}. C'est beau non ?".format(result)
            
        except Exception as e:
            print(e)
            result = "Oups, mon cerveau ne fonctionne plus"
        result = "{}.".format(result) 
        try:
            self.osc_client.sendOsc('/iagotchi/botresponse','{}'.format(response))   
        except:
            pass
        return result
    
    def check_no_lima_option(self, response):
        """
        No use lima preprocessing for the next utterence
        """
        if response and 'nolima' in response.lower():
            response = response.replace('nolima', '')
            self.no_use_lima = True
        return response
    
    #TODO save using_topic_responses dictionnary in a file for another session
    def _save_response_in_file(self, rep, topic, qid):
        """
        For saving response in the topic response file.
        """
        if qid in self.using_topic_responses[topic].keys():
            self.using_topic_responses[topic][qid].append(rep)
        else:
            self.using_topic_responses[topic][qid] = [rep]
        print("using_topic_responses {}".format(self.using_topic_responses[topic][qid]))
        
    def load_responses_pickle_obj(self):
        """
        Load response pickle object.
        If the data/responses.pkl exists return its object else create it and return its object.
        """
        if os.path.exists('data/responses.pkl'):
            with open('data/responses.pkl', 'rb') as f:
                return pickle.load(f)
        else:
            responses_ = {'rencontre':dict(), 'g5':dict()}
            for t in configfile['topic']['list']:
                if os.path.exists('data/{}.txt'.format(t)):
                    with open('data/{}.txt'.format(t), 'r') as f:
                        lines = f.readlines()
                    for i, line in enumerate(lines):
                        if i < len(lines) -1 :
                            responses_[t][i] = [lines[i+1].strip()]
                        else:
                            responses_[t][i] = [lines[0].strip()]
                else:
                    responses_[t] = None
            self.save_responses_pickle_obj(response_)
            #with open('data/responses.pkl', 'wb') as f:
                #pickle.dump(responses_, f, pickle.HIGHEST_PROTOCOL)
            return response_
            
    def save_responses_pickle_obj(self, obj):
        with open('data/responses.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
                
        #if os.path.exists("data/responses_{}.txt".format(topic)): os.remove("data/responses_{}.txt".format(topic))
        
    def _get_similarity(self, text, topic):
        """
        Function for extracting similar question of text from topic data.
        """
        try:
            distance, qid,  transcript_similar, repsimilar, topic_responses = self.similarity.similarity(text, topic, using_topic_responses=None)
            #self.using_topic_responses[topic] = topic_responses
            return distance, qid,  transcript_similar, repsimilar
        except:
            return 0, 5, text, "parlons d'autres choses s'il te plaît"
    
    def _check_bonjour_et_toi_in(self, transcript):
        """
        Check if 'bonjour' and/or 'et toi' in transcript. 
        """
        if self._et_toi_in(transcript):
            transcript_ = "utilisateur renvoyer {}".format(self.user_name)
        else:
            transcript_ = "utilisateur {}".format(self.user_name)
        if any(bn in transcript.lower() for bn in lstbonjour):
            transcript = transcript + " " + transcript_
        else:
            transcript =  transcript_
            
        print("chatscript_externals._check_bonjour_et_toi_in {}".format(transcript))
        return transcript
    
    
    # TODO quand session start et user name dans phrase avec bonjour
    # TODO règle pour "bonjour je m'appelle X"
    def preprocessing(self, transcript):
        """
        Preprocessed the user's question before sending it to the chat engine.
        """
        if not self.check_g5_keywords(transcript):
            print(self.check_g5_keywords(transcript))
            print("externals.preprocessing response {} need_user_name: {} user_name: {}".format(transcript, self.need_user_name, self.user_name))
            if self.need_user_name and self.user_name is None:
                pers = self._person_entity(transcript)
                if not pers is None:
                    self.need_user_name = False
                    self.user_name = pers
                    if self.osc_client is not None:
                        self.osc_client.sendOsc('/iagotchi/session/name','{}'.format(self.user_name))
                    print(pers)
                    self.log.insert("User", "username", pers)
                    transcript = self._check_bonjour_et_toi_in(transcript)
                    
            elif not self.need_user_name and not self.user_name is None:
                self.need_user_name = False
            elif not self.need_user_name and self.user_name is None and self.interaction_counter < 1:
                pers = self._person_entity(transcript)
                if not pers is None:
                    self.need_user_name = False
                    self.user_name = pers
                    if self.osc_client is not None:
                        self.osc_client.sendOsc('/iagotchi/session/name', '{}'.format(self.user_name))
                    print(pers)
                    self.log.insert("User", "username", pers)
                    transcript = self._check_bonjour_et_toi_in(transcript)
            
        self.interaction_counter += 1
        print("externals.preprocessing after response {} need_user_name: {} user_name: {}".format(transcript, self.need_user_name, self.user_name))
        return transcript
            
    def cleanup(self, s):
        s = ''.join(c for c in s if c not in punctuations)
        return RE_STRIP_REFS.sub("", s).strip()
            
    #TODO activer la suppression des mots vides
    def remove_stopwords(self, text):
        text_ = text
        if '-' in text:
            text = text.replace('-', ' ')
        print('before: {}  after remove_stopwords: {}'.format(text_, text))
        text = self.cleanup(text).split()
        #text = [t for t in text if not t in raw_stopword_top_list]
        return " ".join(text)
            
    def run(self, transcript, osc_client=None, osc_self_client=None):
        """
        Take as input a transcript, perform a preprocessing of the text, send to the dialogue system, perform a postraitement of the response, make the voice synthesis of the response and save the data in the log file. Also update the chrono module.
        Input: transcript
        Output: "stop" if user says bye bye else None.
        """
        self.chrono.osc_self_client = osc_self_client
        self.chrono.input_mode = self.input_mode
        print('<<CHRONO IN EXTERNALS>>', self.chrono.input_mode)
        self.osc_client = osc_client
        self.osc_self_client = osc_self_client
        if self.chrono.botresponse_object is None:
            self.chrono.botresponse_object = osc_client
        if self.poesie:
            return None   
        elif self.chrono.waiting_to_stop:
            return None
        elif any(bn in transcript.lower() for bn in lstbonjour) and (self.session_status == 'stop' or self.session_status is None):
            self.startup()
            return '{} __hello__'.format(self.process(transcript))
        elif self.session_status == 'start' and not self.syn.reading:
            response = self.process(transcript)
            if 'lastoutput' in response.lower():
                response = self.last_response
            return response

        return 'stop'
    
    def process(self, transcript):
        """
        To process 
        """
        self._transcript = transcript
        print('no.use_lima {}'.format(self.no_use_lima))

        if self.no_use_lima:
            response = self.postprocessing(self.chatscript.sendAndReceiveChatScript(transcript, "User", self.botname, lima_processing=False))
            self.no_use_lima = False
        else:
            transcript_ = self.remove_stopwords(self.preprocessing(transcript))
            print('chatscript_externals.run after stopwords removing: {}'.format(transcript_))
            response = self.postprocessing(self.chatscript.sendAndReceiveChatScript(transcript_, "User", self.botname, lima_processing=True))
        if self.need_restart_postprocessing:
            response = self.postprocessing(response)
            self.need_restart_postprocessing = False
        synth_response = self.syn.synthese(response)
        self.log.save_in_file(transcript, response)
        if self.need_stop:
            self.stop()
            return "{} _stop_".format(synth_response)
        elif self.start_music:
            self.start_music = None
            return '{} start_music'.format(synth_response)
        elif not self.start_music and not self.start_music is None:
            self.start_music=None
            return '{} stop_music'.format(synth_response)
        else:
            self.chrono.current_response_time = datetime.datetime.now()
            return synth_response
            
    def stop(self):
        self.session_status = 'stop'
        self.chrono.stop()
        
    def check_g5_keywords (self, text):
        """
        Check if there is a G5 keyword in the text.
        """
        print(configfile["g5_sigles"])
        keywords = [keyw for keyw in configfile["g5_sigles"] if keyw in text]
        if len(keywords) > 0:
            return True
        else:
            return False
            
    def _capitalize_text(self, text):
        """
        Function to make the first letters of the words uppercase.
        """
        text = text.split()
        text = [w.capitalize() for w in text]
        return " ".join(text[:])
            
                
            
    def _person_entity(self, text):
        """
        Check if person entity is in text.
        Input: Text
        Output: The entity if it exists otherwise None
        """
        _person_lima = None
        try:
            doc2lima = self.lima.sendAndReceiveLima(text, mode=None)
            npp_words = list()
            for word in doc2lima[3:]:
                if word.split('\t')[9].startswith('NE=Person'):
                    _person_lima = word.split('\t')[1]
                if  word.split('\t')[3].strip() == 'NPP':
                    ner = word.split('\t')[9].strip().split('|')
                    if len(ner) > 2:
                        pos = ner[1].split('=')[1]
                        length = ner[2].split('=')[1]
                    else:
                        pos = ner[0].split('=')[1]
                        length = ner[1].split('=')[1]
                    npp_words.append((word.split('\t')[1].strip(), pos, length))
            if _person_lima is None and len(npp_words) > 0:
                texte = doc2lima[2].split('=')[1].strip()
                for w, p, l in npp_words:
                    w = w.capitalize()
                    texte = texte[0:p-1]+w+texte[p-1+l:]
                doc2lima = self.lima.sendAndReceiveLima(texte, mode=None)
                for word in doc2lima[3:]:
                    if word.split('\t')[9].startswith('NE=Person'):
                        _person_lima = word.split('\t')[1]
        except:
            pass
        return _person_lima
        
    def _NC_entity(self, text):
        """
        Check the presence of a common noun
        Input: Text
        Output: The entity if it exists otherwise None
        """
        _NC_lima = list()
        try:
            doc2lima = self.lima.sendAndReceiveLima(text, mode=None)
            for word in doc2lima[3:]:
                if len(word.split('\t')) > 3 and ('NC' in word.split('\t')[3] or 'NPP' in word.split('\t')[3]) :
                    _NC_lima.append(word.split('\t')[1])

            _NC_lima = [w for w in _NC_lima if w not in all_raw_stopword]
            if len(_NC_lima) > 0:
                if 'mot' in _NC_lima and len(_NC_lima) > 1:
                    return _NC_lima.remove('mot')
                else:
                    return _NC_lima
            else:
                return None
        except:
            return None
        
        
    def _et_toi_in(self, text):
        """
        Check if 'et toi' or 'et vous' are in the text.
        Input: Text
        Output: True if yes else False.
        """
        et_toi = ['et toi', 'et vous']
        _in = [0 for w in et_toi if w in text.lower()]
        if len(_in) == 0:
            return False
        else:
            return True

