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

import os, json

class Rules(object):
    
    def __init__(self):
        self.source_folder = 'ChatScript/RAWDATA/'
        self.iagotchi_folder = os.path.join(self.source_folder, 'IAGOTCHI')
        self.iagotchiG5_folder = os.path.join(self.source_folder, 'IAGOTCHIG5')
        self.files_top = {'iagotchi':['introductions', 'relance'], 'iagotchig5':['introductions', 'relance', 'g5_questions']}
        self.output_iagotchi = 'rules_data_iagotchi.json'
        self.output_iagotchig5 = 'rules_data_iagotchiG5.json'
        self.dict_data = {'iagotchi':{}, 'iagotchig5':{}}
        
    def generateJson(self):
        for bot, lst_top in self.files_top.items():
            for top in lst_top:
                if bot == 'iagotchi':
                    filename = os.path.join(self.iagotchi_folder, '{}.top'.format(top))
                else:
                    filename = os.path.join(self.iagotchiG5_folder, '{}.top'.format(top))
                self.extract_data(filename, bot, top)
        with open(self.output_iagotchi, 'w', encoding='utf8') as fp:
            fp.write(json.dumps(self.dict_data['iagotchi'], indent=4, separators=(',', ': ')))
        with open(self.output_iagotchig5, 'w', encoding='utf8') as fp:
            fp.write(json.dumps(self.dict_data['iagotchig5'], indent=4, separators=(',', ': ')))
        print(self.dict_data)
        
    
                    
                    
                    
    def extract_data(self, filename, bot, top):
        with open(filename, 'r', encoding='utf8') as f:
            for i, line in enumerate(f):
                if line.strip().startswith('#!'):
                    q = line.strip().replace('#!', '')
                    if top in self.dict_data[bot].keys():
                        self.dict_data[bot][top].append(q)
                    else:
                        self.dict_data[bot][top] = [q]
        
if __name__ == "__main__":
    r = Rules()
    r.initialJson()
    #r.generateJson()
