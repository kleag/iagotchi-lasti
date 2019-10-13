#from spacy.lang.fr.examples import sentences 
#import spacy
import re, json, datetime
from chatscript import ChatscriptInstance
import threading
from synthese import Synthese
import socket
from chrono import ChronoThread
from lima import Lima
from similarity import Similarity
import wikipedia
from generator.generator import Generator
import random, os
from nltk.corpus import stopwords
import pickle

 

raw_stopword_top_list = stopwords.words('french')[0:64]

    

print('chatscript_externals load wikipedia module')
wikipedia.set_lang("fr")
#sim = Similarity(using='embeddings')
#generator = Generator('generator/iagotchi.model')



# TODO à remplacer par lima
#nlp = spacy.load('fr')


with open(r'@CMAKE_INSTALL_PREFIX@/data/config.json', 'r') as sv:
    configfile = json.load(sv)
    
try:
    syn = Synthese(configfile['synthesize'])
except:
    syn = Synthese()
    
lstbonjour = ["allo", "allô", "aloha", "bon après-midi", "bonjour", "bonjour et bienvenue", "bonsoir", "c'est bien de vous revoir", "content de te rencontrer", "enchanté", "hella", "hello", "hey", "hey toi", "hiya", "salutations", "salut", "sympa de te rencontrer", "sympa de te voir"]
stpwds = ['qu', 'que', 'qui', 'ne', 'pas', "n'"]
punctuations = '''!()[]{};:"\,<>./?@#$%^&*'''
RE_STRIP_REFS = re.compile("\.?\[\d+\]?")


for wd in stpwds:
    try:
        raw_stopword_top_list.remove(wd)
    except:
        continue
#ext_similarity = Similarity(using=configfile['similarity']['ToUse'])

chrono = ChronoThread(log=None)
chrono.start()
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
        self.startup()
        self.definition = dict()
        self.themes = configfile['themes']
        self.themes_used = list()
        self.chatscriptkeywords = configfile["chatscript_keywords"]
        self.using_topic_responses = None #self.load_responses_pickle_obj()
        try:
            self.botresponse_host = configfile['botresponse']['ip']
            self.botresponse_port = int(configfile['botresponse']['port'])
            self.music_host = configfile['musique']['ip']
            self.music_port = int(configfile['musique']['port'])
        except:
            self.music_port = 5007
        self.start_music = None
        self.definitions_from_db = dict()
        if len(self.themes) > 0:
            for th in self.themes:
                res = self.log.getDefinition(th)
                if not res is None:
                    self.definitions_from_db[th] = res
        self.no_use_lima = False
        
    def startup(self):
        self.log = self.chatscript.start_iagotchi_bot()
        self.chrono.log = self.log
          
        try:
            print('ici ici')
            self.chrono.session_restart_duration = int(configfile['session']['restart'])
            self.chrono.session_stop_duration = int(configfile['session']['stop'])
            self.chrono.session_duration = int(configfile['session']['duration'])
            if self.chrono.session_restart_duration > self.chrono.session_stop_duration:
                sys.exit("[Iagotchi-Bot Error] Value of stop field in session must be less than restart value.")
        except:
            sys.exit("[Iagotchi-Bot Error] Stop, Restart and Duration values must be an integer.")
        self.chrono.start_time = self.chatscript.start_time
        self.chrono.current_response_time = None
        self.chrono.externals = self
        
        self.session_status = 'start'
        #self.chrono.start()
        self.chrono.status = True
        self.need_stop = False
    
    def postprocessing(self, response):
        response = response.lower()
        print("externals.postprocessing response {} need_user_name: {} user_name: {}".format(response, self.need_user_name, self.user_name))
        print("externals.postprocessing: theme already discussed {}".format(len(self.themes_used)))
        if "sessionstart" in response and not self.need_user_name:
            self.need_user_name = True
            response = re.sub('sessionstart', ' ', response)
        elif "sessionstart" in response and self.need_user_name:
            response = re.sub('sessionstart', ' ', response)
            self.need_user_name = False
        elif "lastoutput" in response.lower():
            response = self.last_response
            
        elif "sessionstop" in response.lower():
            response = re.sub('sessionstop', ' ', response)
            self.need_stop = True
        elif "notrule" in response.lower():
            """
            Recherche de question similaire; Recherche de règles pour la question similaire; Si réponse, renvoie réponse
            Sinon renvoie réponse renvoyée pour module de recherche de questions similaires. 
            """
            response_ = re.sub('notrule', ' ', response)
            print('chatscript_externals.postprocessing: response--> {} need to search similar question'.format(response_))
            #distance, qid,  transcript_similar, repsimilar = self.similarity.tfidf_simlarity(self._transcript)
            distance, qid,  transcript_similar, repsimilar = self._get_similarity(self._transcript, 'rencontre')
            print('chatscript_externals.postprocessing similar question found: {}'.format(transcript_similar))
            #response = repsimilar
            response = self.chatscript.sendAndReceiveChatScript(self.preprocessing(transcript_similar), "User", self.botname, lima_processing=True)
            if 'notrule' in response.lower() and repsimilar is None:
                response = re.sub('notrule', ' ', response)
            elif 'notrule' in response.lower() and not repsimilar is None:
                response = repsimilar
            elif not 'notrule' in response.lower():
                self.need_restart_postprocessing = True
                
        elif "wikipedia4generalword" in response.lower():
            response_ = re.sub('wikipedia4generalword', '', response)
            response_ = self._NC_entity(response_)
            print('postprocessing response_ {}'.format(response_))
            if not response_ is None:
                for i, elt in enumerate(response_):
                    if elt.lower() in self.definition.keys():
                        response = self.chatscript.sendAndReceiveChatScript("définition existe déjà  {} dans la base de données {}".format(elt.lower(), self.definition[elt.lower()]), "User", self.botname)
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
                        try:
                            definition = wikipedia.summary(elt.lower(), sentences=1)
                            response = definition
                            self.definition[elt.lower()] = definition
                            if elt.lower() in self.themes:
                                self.log.theme_insertion(elt.lower(), definition)
                                self.themes_used.append(elt.lower())
                            break
                        except:
                            definition = None
                            if i < len(response_) - 1:
                                continue
                            else:
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
            response_ = re.sub('wikipediamocle0', '', response)
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
                try:
                    definition = wikipedia.summary(mot.lower(), sentences=1)
                    response = definition
                    self.definition[mot.lower()] = definition
                    if mot.lower() in self.themes:
                        self.log.theme_insertion(mot.lower(), definition)
                        self.themes_used.append(mot.lower())
                except:
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
                try:
                    definition = wikipedia.summary(mot.lower(), sentences=1)
                    response = definition
                    self.definition[mot.lower()] = definition
                    if mot.lower() in self.themes:
                        self.log.theme_insertion(mot.lower(), definition)
                        #self.themes_used.append(mot.lower())
                except:
                    response = self.chatscript.sendAndReceiveChatScript("relance question", "User", self.botname)

        elif "wikipediamocle1" in response.lower():
            """
            L'utilisateur donne une définition. Le bot doit l'enregistrer.
            """
            print('chatscript_externals.postprocessing.wikipediamocle1 {}'.format(response))
            response_ = re.sub('wikipediamocle1', '', response)
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
                try:
                    definition = wikipedia.summary(mot.lower(), sentences=1)
                    response = definition
                    self.definition[mot.lower()] = definition
                    if mot.lower() in self.themes:
                        self.log.theme_insertion(mot.lower(), definition)
                        #self.themes_used.append(mot.lower())
                except:
                    response = self.chatscript.sendAndReceiveChatScript("relance question", "User", self.botname)
                #response = self.chatscript.sendAndReceiveChatScript("relance question", "User", "iagotchi")
                
                    
        elif "wikipediamotcleinitial" in response.lower():
            response_ = re.sub('wikipediamotcleinitial', '', response)
            response_ = self.check_no_lima_option(response_)
            mot = response_.split()[-1].lower()
            print('postprocessing response_ {}'.format(response_))
            if mot.lower() in self.definition.keys():
                response = self.chatscript.sendAndReceiveChatScript("définition existe déjà  {} dans la base de données {}".format(mot, self.definition[mot]), "User", self.botname)
                response = response.split()
                index_ = [response.index(keyword) for keyword in self.chatscriptkeywords if keyword in response]
                if len(index_) > 0:
                    response = ' '.join(response[0:index_[0]])
                else:
                    response = ' '.join(response)
            elif len(self.themes_used) >= 3:
                response = self.chatscript.sendAndReceiveChatScript("relance question", "User", self.botname)
            elif not mot in self.definitions_from_db.keys():
                try:
                    definition = wikipedia.summary(mot, sentences=1)
                    print('wikipedia definition of {} is {}'.format(mot, definition))
                    self.definitions_from_db[mot] = [definition]
                except:
                    pass
                response = response_.split()[0:-1]
                response = " ".join(response)
                
        elif "question4poesie" in response.lower():
            response_ = re.sub('question4poesie', 'Un instant', response)
            response_ = self.check_no_lima_option(response_)
            synthfile = syn.synthese(response_)
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
                
            except:
                result = "Oups, mon cerveau ne fonctionne plus"
            response = "{}.".format(result)               
                
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
            response = response.replace('**stopmusique', '')
            self.start_music = False
            
                   
        response = self.check_no_lima_option(response)
        print("externals.postprocessing after response {} need_user_name: {} user_name: {}".format(response, self.need_user_name, self.user_name))
        self.last_response = response
        return response
    
    def check_no_lima_option(self, response):
        """
        No use lima preprocessing for the next utterence
        """
        if 'nolima' in response.lower():
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
        distance, qid,  transcript_similar, repsimilar, topic_responses = self.similarity.similarity(text, topic, using_topic_responses=None)
        #self.using_topic_responses[topic] = topic_responses
        return distance, qid,  transcript_similar, repsimilar
    
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
            
    def run(self, transcript, osc_client):
        """
        Take as input a transcript, perform a preprocessing of the text, send to the dialogue system, perform a postraitement of the response, make the voice synthesis of the response and save the data in the log file. Also update the chrono module.
        Input: transcript
        Output: "stop" if user says bye bye else None.
        """
        if self.chrono.botresponse_object is None:
            self.chrono.botresponse_object = osc_client
            
        print('session_status {}'.format(self.session_status))
        if not self.session_status == 'stop':
            return self.process(transcript)
        elif any(bn in transcript.lower() for bn in lstbonjour):
            if self.session_status == 'stop':
                print('session_status in any {}'.format(self.session_status))
                self.startup()
                print('session_status in any {}'.format(self.session_status))
                return self.process(transcript)
            
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
        synth_response = syn.synthese(response)
        self.log.save_in_file(transcript, response)
        if self.need_stop:
            self.chrono.stop()
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
        #self.save_responses_pickle_obj(self.using_topic_responses)
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
        Check the presence of a person entity
        Input: Text
        Output: The entity if it exists otherwise None
        """
        try:
            
            doc2lima = self.lima.sendAndReceiveLima(text)
            _person_lima = [w for w, p in doc2lima if p == "NPP" and w.lower() not in lstbonjour]
            if len(_person_lima) > 0:
                return _person_lima[0]
            else:
                return None
        except:
            None
        
    def _NC_entity(self, text):
        """
        Check the presence of a common noun
        Input: Text
        Output: The entity if it exists otherwise None
        """
        try:
            doc2lima = self.lima.sendAndReceiveLima(text)
            _NC_lima = [w for w, p in doc2lima if p == "NC" or w in self.themes]
            #_NC_lima = []
            if len(_NC_lima) > 0:
                if 'mot' in _NC_lima[0] and len(_NC_lima) > 1:
                    return _NC_lima.remove('mot')
                else:
                    return _NC_lima
            else:
                return None
        except:
            return None
        
        ## using spacy
        #text = self._capitalize_text(text)
        #doc = nlp(text)
        #_person = [token.text for token in doc if token.pos_ == "PROPN"]
        #if len(_person) > 0:
            #return _person[0]
        #else:
            #return None
        
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

