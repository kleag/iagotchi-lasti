#
# /*
#     Copyright 2020 CEA LIST
#     This file is part of Iagotchi-bot.
#     Iagotchi-bot is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#     Iagotchi-bot is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#     You should have received a copy of the GNU Affero General Public License
#     along with Iagotchi-bot.  If not, see <http://www.gnu.org/licenses/>
# */
#
"""
This script is used to send queries to the LIMA linguistic analyzer
"""

try:
    import requests
except:
    pass
import argparse, json, datetime

with open(r'@CMAKE_INSTALL_PREFIX@/data/config.json', 'r') as sv:
    configfile = json.load(sv)


class Lima(object):
    
    def __init__(self):
        self.address = configfile['lima']['address']
        self.port = int(configfile['lima']['port'])
        self.response = None
        self.url = 'http://{}:{}/?lang=fre&pipeline=deep'.format(self.address,self.port)
        print('Lima init')
        #self.chatfile = r'@ChatScriptInstallDir@/chat.txt'
    
    
    def testLimaserver(self):
        #params = (('lang', 'fre'), ('pipeline', 'deep'),)
        texte = u'%s' % ('je')
        texte = str.encode(texte)
        self.response = requests.post(self.url, data=texte)
        return self.response
    
    
    def _get_token_pos(self, tokens):
        """
        Function to retrieve each word with its pos.
        input: tokens from lima server
        output: list of words
        """
        words = []
        for line in tokens:
            if '\t' in line and not "ID\tFORM\tLEMMA\tUPOS" in line:
                line = line.split('\t')
                words.append((line[1], line[3]))
        return words
                
                
    def _get_word_lemma(self, tokens):
        """
        Function to retrieve lemma of only one word.
        input: tokens from lima server 
        output: lemma
        """
        word = None
        for line in tokens:
            if '\t' in line and not "ID\tFORM\tLEMMA\tUPOS" in line:
                line = line.split('\t')
                word = "{}".format(line[2])
        return word
        
        
                
    def _get_token_pos_lemma(self, tokens, only_lemma=False):
        """
        Function to retrieve each word with its lemma and pos from a list of words.
        input: tokens from lima server
        output: a tabbed triple of original word, tag, lemma
        """
        words = ""
        for line in tokens:
            if '\t' in line and not "ID\tFORM\tLEMMA\tUPOS" in line:
                line = line.split('\t')
                if only_lemma:
                    words += "\t{}".format(line[2])
                else:
                    words += "\t{}\t{}\t{}\n".format(line[1], line[3], line[2])

        return words
    
    def _lima_tagger(self, chatfile):
        chatfile = open(chatfile, 'r').read()
        with open('tt.txt', 'a') as f:
            f.write("{}\n".format(chatfile))
        return self.sendAndReceiveLima(chatfile.strip(), mode='word_pos_lemma')
    
    def text_lima_tagger(self, text):
        if "-" in text: text.replace('-', ' ')
        text = " ".join(self.sendAndReceiveLima(text, mode='text2lemma').split('\t'))
        #text = u'%s' % (text)
        return text

    
    def _process_text(self, tokens):
        words = []
        for line in tokens:
            if '\t' in line and not "ID\tFORM\tLEMMA\tUPOS" in line:
                line = line.split('\t')
                words.append(line[2])
        words = " ".join(words[:])
        return words
    
    def requests4lima(self, text, headers):
        if configfile['what_run'] == 'similarity':
            code = 0
            duration = 0
            rep = None
            current_time = datetime.datetime.now()
            while code != 200 and duration < 60:
                try:
                    rep = requests.post(self.url, data=text, headers=headers)
                except:
                    pass
                code = rep.status_code
                duration = (datetime.datetime.now() - current_time).total_seconds()
        else:
            rep = requests.post(self.url, data=text, headers=headers)
        return rep
                
    
    
    def sendAndReceiveLima(self, text, mode="word_pos"):
        """
        Send text to Lima sercer and Receive text processed. 
        mode: word_pos, word_pos_lemma, speelcheck, lemma, text2lemma
        """
        #print('lima.sendAndReceiveLima: {}'.format(text))
        try:
            text = u"%s" % (text)
        except:
            pass
        text = str.encode(text)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        rep = self.requests4lima(text, headers)
        rep = rep.json()
        #print(rep)
        rep = rep['tokens']
        #print(rep)
        if mode == "word_pos":
            return self._get_token_pos(rep)
        elif mode == "word_pos_lemma":
            return self._get_token_pos_lemma(rep)
        elif mode == "lemma":
            return self._get_word_lemma(rep)
        elif mode == "text":
            return self._process_text(rep)
        elif mode == "text2lemma":
            return self._get_token_pos_lemma(rep, only_lemma=True)
        elif mode is None:
            return rep
        
     
     

        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('chatfile', help='process chat file')
    
    args = parser.parse_args()
    lima = Lima()
    #print(lima.sendAndReceiveLima("bonjour"))
    print(lima._lima_tagger(args.chatfile))
    

        
        
