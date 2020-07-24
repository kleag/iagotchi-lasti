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

import os, json, tarfile, smart_open

class ProcessLog(object):
    
    def __init__(self, log_folder):
        self.botnames = ['iagotchi', 'iagotchig5']
        if os.path.exists(log_folder):
            self.log_folder = log_folder
        else:
            sys.exit('[ProcessLog failed: {} does not exists]'.format(log_folder))
        self.botfolder = {'iagotchi':os.path.join(self.log_folder, 'iagotchi'), 'iagotchig5':os.path.join(self.log_folder, 'iagotchiG5')}
        for bot, folder in self.botfolder.items():
            if not os.path.exists(folder):
                print('[ProcessLog warning: {} does not exists]'.format(folder))
        self.bot_data = {'iagotchi':dict(), 'iagotchig5':dict()}
        self.datas = list()
        
        
    def get_content_from_file(self, bot, filename):
        print('[ProcessLog Info: get_content_from: {}]'.format(filename))
        with open(filename, encoding='utf8') as f:
            for line in f:
                line_ = line.strip()
                line = line_.split('\t')
                print(line)
                if len(line) > 0 and 'User:' in line_ and 'Iagotchi:' in line_:
                    question = line[1].strip().replace('User:', '')
                    question = question.strip()
                    if len(question) > 0:
                        self.datas.append(question)
                        response = line[2].strip().replace('Iagotchi:', '')
                        response = response.strip()
                        if len(response) > 0:
                            self.datas.append(response)
                            self.bot_data[bot][question] = response
                            
    def browse_folder(self, bot):
        if os.path.exists(self.botfolder[bot]):
            for folder in os.listdir(self.botfolder[bot]):
                folder = os.path.join(self.botfolder[bot], folder)
                if os.path.exists(folder):
                    for filename in os.listdir(folder):
                        filename=os.path.join(folder, filename)
                        self.get_content_from_file(bot, filename)
                
                
    def run(self):
        for botname in self.botnames:
            self.browse_folder(botname)
            with open('{}/{}.json'.format(self.log_folder, botname), 'w', encoding='utf8') as fp:
                fp.write(json.dumps(self.bot_data[botname], ensure_ascii=False, indent=4, separators=(',', ': ')))
        if not os.path.isfile('data/texts.sent'):
            mode = 'w'
        else:
            mode = 'a'
        with open('data/texts.sent', mode, encoding='utf8') as f:
            f.write('\n'.join(self.datas))
        
                
    def initial_data(self, filename, output):
        content = dict()
        with open(filename, 'r', encoding='utf8') as f:
            for line in f:
                if line.strip().startswith('#!'):
                    line = line.strip().split('#!')
                    for l in line:
                        self.datas.append(l)
                    question = line[1].strip()
                    response = '#!'.join(line[2:])
                    content[question] = response
        with open(output, 'w', encoding='utf8') as fp:
            fp.write(json.dumps(content, ensure_ascii=False, indent=4, separators=(',', ': ')))
        with open('data/texts.sent', 'w', encoding='utf8') as f:
            f.write('\n'.join(self.datas))
            
    def initialJson(self):
        self.initial_data('data/rencontre27092019.txt', 'data/rencontre27092019.json')
        self.initial_data('data/g527092019.txt', 'data/g527092019.json')
        
    #def write_read_texts(self, data, mode='w'):
        #if mode == 'w':
            #with smart_open.smart_open('data/texts.sent', 'wb') as f:
                #for line in data:
                    #if len(line.strip()) > 0:
                        #f.write(line.encode("utf-8"))
            #return None
        #elif mode == 'a':
            #assert os.path.isfile("data/texts.sent"), "data/texts.sent unavailable"
            #all_docs = []
            #with smart_open.smart_open('aclImdb/alldata-id.txt') as alldata:
            #tar = tarfile.open(filename, mode='r')
            #tar.extractall()
            #tar.close()
            
        
    def merge_texts_sent(self):
        with open('data/texts.sent', 'a', encoding='utf8') as f:
            f.write('\n')
            f.write('\n'.join(self.datas))
            
    def loadJsonContent(self, filename):
        with open(filename) as f:
            data = json.load(f)
        return data
            
    def append_data(self):
        for bot, data in self.bot_data.items():
            if bot == 'iagotchi':
                filename = 'data/rencontre27092019.json'
            elif bot == 'iagotchig5':
                filename = 'data/g527092019.json'
            if os.path.isfile(filename):
                contents = self.loadJsonContent(filename)
                contents.update(data)
                with open(filename, 'w', encoding='utf8') as fp:
                    fp.write(json.dumps(contents, ensure_ascii=False, indent=4, separators=(',', ': ')))
        
        
        
if __name__ == "__main__":
    pl = ProcessLog('data/logs/')
    #pl.initialJson()
    pl.run()
    pl.merge_texts_sent()
    pl.append_data()
                        
            
