import os, argparse
import gensim
from nltk.tokenize import word_tokenize
from gensim import corpora
from nltk.corpus import stopwords
from lima import Lima
import codecs
import sys, json
import sent2vec
import numpy as np
import pickle, bz2, re
from scipy.spatial.distance import cdist
from collections import Counter
import random
from random import randint

print('similarity module loading')
raw_stopword_list = stopwords.words('french')
print('similarity Lima connection')
lima = Lima()


class ProcessCorpus(object):

    """
    Used to process the questions in the corpus.
    """

    #def __init__(self, corpus_dir, FOLDER):
        #self.corpus_dir = corpus_dir
        #self.file_dir = os.path.join(self.corpus_dir, FOLDER)

    def tokenize(self, question, to_lower=True):
        question = question.strip()
        if to_lower:
            question = question.lower()
        return question

    def tokenize_questions(self, questions, to_lower=True):
        return [self.tokenize(question, to_lower) for question in questions]
    
    def read_corpus(self, corpus_file):
        print("load data from {}".format(corpus_file))
        data = []
        with open(corpus_file, 'r') as f:
            for line in f:
                data.append(line.strip())
        questions = self.tokenize_questions(data)
        print("load data done, number of documents {}".format(len(data)))
        return questions


class BuildTFIDF(object):
    """
    This class is used for building tfidf models.
    """
    
    
    def __init__(self, model_dir):
        self.model_dir = model_dir
        self.file_dict = os.path.join(self.model_dir, 'iagotchi.dict')
        self.file_mmcorpora = os.path.join(self.model_dir, 'iagotchi.mm')
        self.file_index = os.path.join(self.model_dir, 'iagotchi.index')
        self.lst_file = [self.file_dict, self.file_mmcorpora, self.file_index]
    
    def remove_files_if_exists(self):
        """
        Remove model files if they exist.
        """
        if os.path.exists(self.file_dict): os.remove(self.file_dict)
        if os.path.exists(self.file_mmcorpora): os.remove(self.file_mmcorpora)
        if os.path.exists(self.file_index): os.remove(self.file_index)
        
    def remove_stopwords(self, question):
        """
        Remove stopwords in a question.
        """
        question = [w for w in question if not w in raw_stopword_list]
        return " ".join(question[:])
            
        
    def buildtfidf(self, questions):
        """
        Build tfidf models tfidf models from texts pre-processed with lima. 
        Stopwords are initially removed.
        Input: texts pre-processed with lima
        Output: a list of the names of each saved model file.
        """
        self.remove_files_if_exists()
        gen_docs = [[w.lower() for w in word_tokenize(self.remove_stopwords(doc), language='french')]
                        for doc in questions]
        print("buildtfidf - taille de gen {}".format(len(gen_docs)))
        dictionnaire = gensim.corpora.Dictionary(gen_docs)
        dictionnaire.save(self.file_dict)  # store the dictionary, for future reference
        corpus = [dictionnaire.doc2bow(gen_doc) for gen_doc in gen_docs]
        corpora.MmCorpus.serialize(self.file_mmcorpora, corpus)
        tf_idf = gensim.models.TfidfModel(corpus)
        sims = gensim.similarities.Similarity(self.model_dir+'/',tf_idf[corpus], num_features=len(dictionnaire))
        sims.save(self.file_index)
        
        return self.lst_file
        
        
class TfidfSimilarity(object):
    """
    This class is used to calculate the semantic distance between an input question and the existing questions in the corpus.
    """
    
    def __init__(self):
        self.pc = ProcessCorpus()
        self.model_dir = "data/tfidf"
        self.file_dict = os.path.join(self.model_dir, 'iagotchi.dict')
        self.file_mmcorpora = os.path.join(self.model_dir, 'iagotchi.mm')
        self.file_index = os.path.join(self.model_dir, 'iagotchi.index')
        self.lst_file = [self.file_dict, self.file_mmcorpora, self.file_index]
        self.dictionnaire, self.corpus, self.tf_idf, self.sims = self.load_tfidf_corpus()
        with open("data/rencontre.txt", 'r', encoding='utf8') as f:
            self.lines = f.readlines()
        
    
    def load_tfidf_corpus(self):
        """
        For loading all tfidf models from the filename given as input.
        """
        dictionnaire = gensim.corpora.Dictionary.load(self.lst_file[0])
        corpus = gensim.corpora.MmCorpus(self.lst_file[1])
        tf_idf = gensim.models.TfidfModel(corpus)
        sims = gensim.similarities.Similarity.load(self.lst_file[2])

        return dictionnaire, corpus, tf_idf, sims
    
    def remove_stopwords(self, question):
        """
        Remove stopwords in a question.
        """
        question = [w for w in question if not w in raw_stopword_list]
        return " ".join(question[:])
    
    def getSimilarText(self, texte, dictionnaire, corpus, tf_idf, sims, top=1):
        #dictionnaire, corpus, tf_idf, sims = self.load_tfidf_corpus(fdict, fcorpora, findex) #  = gensim.corpora.Dictionary.load('model.save/labforsims2.dict')
        texte_lima = lima.sendAndReceiveLima(texte, mode='text')
        if not texte_lima:
            texte_lima = texte
        texte = self.remove_stopwords(texte_lima)
        query_doc = [w.lower() for w in word_tokenize(texte)]
        query_doc_bow = dictionnaire.doc2bow(query_doc)
        query_doc_tf_idf = tf_idf[query_doc_bow]
#        print(query_doc_tf_idf)
        indice_m = max(sims[query_doc_tf_idf])
        ii=1
        for i in sims[query_doc_tf_idf]:
            if i==indice_m:
                indice=ii
            ii+=1
        indice = indice -1
        return indice, indice_m

    def tfidf_simlarity(self, texte, top=1):
        indice, prob = self.getSimilarText(texte, self.dictionnaire, self.corpus, self.tf_idf, self.sims, top)
        if indice + 1 >= len(self.lines):
            repsimilar = None
        else:
            repsimilar = self.lines[indice+1]
        return prob, indice, self.lines[indice], repsimilar

class sent2vecProcess():
    
    def __init__(self, currentdirectory):
        print("Init sentences embeddings \n")
        self.modelDir = os.path.join(currentdirectory, "embeddings")
        self.sent2vecValues = dict()
        self.lima = lima
        if not os.path.exists(self.modelDir):
            os.makedirs(self.modelDir)
            
        # A décommenter pour entraîner un modèle embeddings sur ses propres données.
        #sent2vec_path = os.getenv("SENT2VEC")
        
        #if sent2vec_path is None:
            #sys.exit("[Iagotchi Error] You have to configure sent2vec in the environment variables under the SENT2VEC name")
        #elif not os.path.exists(sent2vec_path):
            #sys.exit("[Iagotchi Error] Environment variable {} does'nt exist".format(sent2vec_path))
        #else:
            #self.SENT2VEC_EXEC_PATH = os.path.abspath(os.path.join(sent2vec_path, "fasttext"))
            #print("SENT2VEC executable found: {}".format(self.SENT2VEC_EXEC_PATH))
            
        try:
            with codecs.open('data/config.json', 'r') as cf:
                self.configurations = json.load(cf)
            #self.configurations = self.configurations['sent2vec']
        except Exception as e:
            sys.exit("[Iagotchi Error] config.json file is not found {}".format(e))
        try:
            parameters = self.configurations['sent2vec']
        except:
            parameters = {"data":"Data/all_text.txt", "epoch":15, "lr":0.1, "wordNgrams":2, "minCount":1, "bucket":4000, "dim":300, "loss":"ns", "output":"allsent2vec", "embeddings": "data/fr_model.bin"}
        for param, value in parameters.items():
            if param !="data":
                try:
                    self.sent2vecValues[param] = self.configurations['sent2vec'][param]
                except:
                    self.sent2vecValues[param] = value
        self.model_name = self.sent2vecValues['embeddings']
        self.model = sent2vec.Sent2vecModel()
        #print('load model  {}'.format(modelfile))
        self.model.load_model(self.model_name, inference_mode=True)
        
    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r"'", "e ", text)
        text = re.sub(r"-", " ", text)
        text = re.sub(r"[-()«<>»\"#/@;:<>{}`+=~|.!?,]", "", text)
        return text
            
    def getQuestion(self, q):
        if q and q.startswith('#!'):
            q = q.split('#!')[1]
        return q
    
    def lima_process(self, q):
        return self.lima.text_lima_tagger(q)
            
    def getText(self, file_, topic):
        """
        Si topic == g5, on récupère les questions avec un id impaire dans le fichier. Les réponses étant à l'id pair.
        Si topic == rencontre, on récupère tout le contenu du fichier. 
        """
        if os.path.exists(file_):
            text = list()
            ids = list()
            with open(file_, 'r') as in_stream:
                for idline, line in enumerate(in_stream):
                    if line.strip() and line.startswith('#!'):
                        line = self.getQuestion(line.strip())
                        line = self.clean_text(line)
                        line = self.lima_process(line)
                        text.append(line.strip())
                        ids.append(idline)

                numpy_text = np.array(text) # for line in text
                numpy_ids = np.array(ids)
            return text, numpy_text, numpy_ids
        else:
            sys.exit('[Iagotchi Error] {} does not exist'.format(file_))
            
    def data_sent2vec(self, inpufile):
        self.sent2vecValues["data"] = inputfile
        command="{} sent2vec -input {} -output {} -lr {} -epoch {} -wordNgrams {} -minCount {} -bucket {} -dim {} -loss {}".format(self.SENT2VEC_EXEC_PATH, self.sent2vecValues["data"], os.path.join(self.modelDir, self.sent2vecValues['output']), self.sent2vecValues['lr'], self.sent2vecValues['epoch'], self.sent2vecValues['wordNgrams'], self.sent2vecValues['minCount'], self.sent2vecValues['bucket'], self.sent2vecValues['dim'], self.sent2vecValues['loss'])
        print("command for shell {}".format(command))
        s = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                              shell=True)
        p,e = s.communicate()
        if p:
            print("sent2vec for all data has been processed \n")
        else:
            sys.exit("[Iagotchi Error] sent2vec for all data failed")
            
            
    def topic_sent2vec(self, topic, filename):
        #for classe in self.classes:
        filename = filename
        
        vector_name = "{}.{}".format(topic.lower(),"bin")
        classe_model = self.encode(self.model_name, filename, topic.lower())
        self.store_vector(classe_model, vector_name)
        
    def store_vector(self, vectors, vector_name):
        if os.path.exists("{}/{}".format(self.modelDir, vector_name)):
            os.remove("{}/{}".format(self.modelDir, vector_name))            
        pickle.dump(vectors,  bz2.open(os.path.abspath("{}/{}".format(self.modelDir, vector_name)),  'wb' ))
        
    def encode(self, modelfile, file_path, topic):
        """
        Encode all the sentences of a text as vectors.
        Arguments:
            text:  a unicode object containing multiple sentences.
        Return:
            A dict with the keys 'sent' and 'vec'. The value of 'sent' is a NumPy
            array with the individual sentences of the provided text (as unicode
            objects). The value of 'vec' is a NumPy array of numerical vectors, one
            vector for each sentence in 'sent'.
        """
        # If 'text' blank: sent=[], vec=array([], shape=(0, 4800), dtype=float32)
        #global model
        
        sent_emb, sent_numpy, sent_ids = self.getText(file_path, topic)
        vec = self.model.embed_sentences(sent_emb)
        return dict(sent=sent_numpy, ids=sent_ids, vec=vec)
    
    def run(self):
        for topic in self.configurations['topic']['list']:
            print("{} topic vector calculation \n".format(topic))
            if os.path.exists(self.configurations['topic'][topic]):
                self.topic_sent2vec(topic, self.configurations['topic'][topic])
            else:
                sys.exit("[Iagotchi Error] {} file doesn't not exist.".format(self.configurations['topic'][topic]))
            
            
class EmbeddingsSimilarity(object):
    
    def __init__(self, lima=None):
        try:
            with codecs.open('data/config.json', 'r') as cf:
                self.configurations = json.load(cf)
        except Exception as e:
            sys.exit("[Iagotchi Error] config.json file is not found {}".format(e))
            
        if lima is not None:
            self.lima = lima
        self.currentdirectory = os.path.join(os.getcwd(),"data") 
        self.modelDir = os.path.join(self.currentdirectory, "embeddings")
        print('similarity.EmbeddingsSimilarity: modelDir is {}'.format(self.modelDir))
        self.sentences_embeddings = dict()
        for topic in self.configurations['topic']['list']:
            with bz2.open(os.path.join(self.modelDir, '{}.bin'.format(topic.lower()))) as f:
                self.sentences_embeddings[topic.lower()] = pickle.load(f)
        self.allmodel = sent2vec.Sent2vecModel()
        print('similarity.EmbeddingsSimilarity fr_model loading...')
        if os.path.exists(os.path.join(os.getcwd(), self.configurations['sent2vec']['embeddings'])):
            modelfile = os.path.join(os.getcwd(), self.configurations['sent2vec']['embeddings'])
            self.allmodel.load_model(modelfile)
            print('similarity.EmbeddingsSimilarity fr_model loaded ...')
        try:
            self.k_sorted = int(self.configurations['similarity']['k'])
        except:
            self.k_sorted = 2
        for topic in self.configurations['topic']['list']:
            print('similarity.EmbeddingsSimilarity {} loading...'.format(topic))
            if topic == "rencontre":
                self.rtexts, self.rnumpy_texts, self.rnumpy_ids, self.renconte_responses = self.getText(self.configurations['topic'][topic], topic)
            elif topic == 'g5':
                self.stexts, self.snumpy_texts, self.snumpy_ids, self.g5_responses = self.getText(self.configurations['topic'][topic], topic)
        self.using_topic_responses = None
                
        
            
    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r"'", "e ", text)
        text = re.sub(r"-", " ", text)
        text = re.sub(r"[-()«<>»\"#/@;:<>{}`+=~|.!?,]", "", text)
        return text
    
    def getQuestion(self, q):
        if q and q.startswith('#!'):
            q = q.split('#!')
            responses = q[2:]
        return q[1], responses
    
    def lima_process(self, q):
        return self.lima.text_lima_tagger(q)
            
    def getText(self, file_, topic):
        """
        Si topic == g5, on récupère les questions avec un id impaire dans le fichier. Les réponses étant à l'id pair.
        Si topic == rencontre, on récupère tout le contenu du fichier. 
        """
        if os.path.exists(file_):
            text = list()
            ids = list()
            responses = dict()
            with open(file_, 'r') as in_stream:
                for idline, line in enumerate(in_stream):
                    if line.strip():
                        line, resp = self.getQuestion(line.strip())
                        line = self.clean_text(line)
                        text.append(line.strip())
                        ids.append(idline)
                        responses[idline] = resp

                numpy_text = np.array(text) # for line in text
                numpy_ids = np.array(ids)
            return text, numpy_text, numpy_ids, responses
        else:
            sys.exit('[Iagotchi Error] {} does not exist'.format(file_))
      
    def _is_blank(self, s):
        return not bool(s.strip())
    
    def getSimilar(self, texte, topic):
        texte = self.clean_text(texte)
        texte = self.lima_process(texte)

        record = self.sentences_embeddings[topic.lower()]
        #print(record)
        if self._is_blank(texte):
            return dict(sent=[], dist=[]), topic.lower()
        query_vec = self.allmodel.embed_sentences([texte])
        #print(query_vec)
        distances = cdist(query_vec, record['vec'], 'cosine')[0]
        knn_indices = distances.argsort()[:self.k_sorted].tolist()
        s = record['sent'][knn_indices].tolist()
        s_ids = record['ids'][knn_indices].tolist()
        #print(s_ids)

        d = distances[knn_indices].tolist()
        return dict(sent=s, ids=s_ids, dist=d), topic.lower()
    
    def embeddings_similarity(self, texte, topic):
        """
        Calculate the semantic similarity between a given question and the set of questions in a given category.
        Input: question and category of questions
        Output: distance with the similar question found, id of similare question from category file, similar question found and its response.
        """
        print('simil using {}'.format(self.using_topic_responses))
        similar, topic = self.getSimilar(texte, topic)
        response_file = "data/responses_{}.txt".format(topic)
        if topic == "rencontre":
            q_similar = similar['sent'][0]
            if similar['ids'][0]+1 < len(self.rtexts):
                r_similar = self.renconte_responses[similar['ids'][0]]  #self.rtexts[similar['ids'][0]+1]
            else:
                r_similar = self.rtexts[0]
            dist = similar['dist'][0]
        elif topic == "g5":
            q_similar = similar['sent'][0]
            r_similar = self.g5_responses[similar['ids'][0]]
            dist = similar['dist'][0]
              
        if r_similar and isinstance(r_similar, list) and len(r_similar) > 0:
            i = randint(0, len(r_similar) - 1)
            r_similar = r_similar[i]
                
        return dist, similar['ids'][0], q_similar, r_similar
        
class Similarity(object):
    
    def __init__(self, using='embeddings', lima=None):
        if lima is not None:
            self.lima = lima
        if using.lower() == 'tfidf':
            self.sim = TfidfSimilarity()
        elif using.lower() == 'embeddings':
            self.sim = EmbeddingsSimilarity(lima=self.lima)
        #print(self.sim.texts)
        self.using = using.lower()
        
        
        
        
    def similarity(self, transcript, topic, using_topic_responses=None):
        self.sim.using_topic_responses = using_topic_responses
        if self.using == 'tfidf':
            return self.sim.tfidf_simlarity(transcript)
        elif self.using == 'embeddings':
            distance, qid,  transcript_similar, repsimilar = self.sim.embeddings_similarity(transcript, topic)
            return distance, qid,  transcript_similar, repsimilar, self.sim.using_topic_responses
            
                
if __name__ == "__main__":

    sv = sent2vecProcess("data")
    sv.run()
    

    
    
