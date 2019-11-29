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
            #json.dump(self.dict_data['iagotchig5'], fp)
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
    r.generateJson()
