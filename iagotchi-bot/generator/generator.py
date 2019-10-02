# -*- coding: utf-8 -*-
from __future__ import print_function, division
import torch
from torch.autograd import Variable
import sys, osc, os

this_dir_path = os.path.dirname(os.path.realpath(__file__)) 


class Generator:

    def __init__(self, model_filename, default_allowed_filename=None, osc_server_port=5006, osc_client_host='127.0.0.1', osc_client_port=5005):
        self.osc_server_port = osc_server_port
        self.osc_client_host = osc_client_host
        self.osc_client_port = osc_client_port
        self.osc_client = osc.Client(osc_client_host, osc_client_port)
        self.osc_server = osc.Server(host='0.0.0.0', port=osc_server_port, callback=self.osc_server_message)
        self.osc_server.run(non_blocking=True)
        
        self.osc_client.send("/generator/ready")
        
        self.model = torch.load(model_filename, map_location=lambda storage, loc: storage, encoding='utf8')
        if default_allowed_filename is None:
            self.allowed = set(self.model.dictionary.idx2word)
        else:
            self.allowed = set(open(default_allowed_filename).read().split('\n'))
            self.allowed.update('.,!:;')
            
        print("Generator Ready")

    def disallow(self, words):
        self.allowed.difference_update(words)
        print('main' in self.allowed)

    def allow(self, words):
        self.allowed.update(words)

    def generate(self, num, prime='', temperature=0.7, min_length=20, end_at=['<eos>', '</p><p>']):
        model = self.model
        result = []
        ntokens = len(model.dictionary.idx2word)
        model.eval()
        hidden = model.init_hidden(1)
        inpt = Variable(torch.rand(1, 1).mul(ntokens).long())#, volatile=True)
        for word in prime.split():
            result.append(word)
            inpt.data[0, 0] = model.dictionary.word2idx[word]
            _, hidden = model(inpt, hidden)
        allowed_set = set()
        for word in self.allowed:
            if word in allowed_set:
                continue
            if word in model.dictionary.word2idx:
                allowed_set.add(model.dictionary.word2idx[word])
            if word.capitalize() in model.dictionary.word2idx:
                allowed_set.add(model.dictionary.word2idx[word.capitalize()])
        allowed_ids = torch.LongTensor(list(allowed_set))
        for i in range(num):
            output, hidden = model(inpt, hidden)
            word_weights = output.squeeze().data.div(temperature).exp().cpu()
            selected_weights = word_weights[allowed_ids]
            # word_idx = torch.multinomial(word_weights, 1)[0]
            # word_idx = torch.multinomial(word_weights[1:], 1)[0] + 1
            idx = torch.multinomial(selected_weights, 1)[0]
            word_idx = allowed_ids[idx]
            inpt.data.fill_(word_idx)
            word = model.dictionary.idx2word[word_idx]
            result.append(word)
            if word in end_at and len(result) > min_length:
                break
        return result
    
    def osc_server_message(self, message):
        print("message entrant {}".format(message))
        if message == '/generate':
            result = self.generate(200, prime='<eos>', temperature=0.9)
            thetext = ' '.join([x for x in result if x != '<eos>'])
            thetext = ("   " + thetext + "   ").strip('<eos>')
            thetext = thetext.replace("(", " ")
            thetext = thetext.replace(")", " ")
            thetext = thetext.strip(';')
            print(thetext)
            self.osc_client.send("/generator/result "+thetext);
        elif message == '/exit':
            self.osc_server.shutdown()
            sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        Generator(this_dir_path+'/iagotchi.model');
    elif len(sys.argv) == 4:
        Generator(this_dir_path+'/iagotchi.model',int(sys.argv[1]), sys.argv[2], int(sys.argv[3]))
    else:
        print('usage: %s <osc-server-port> <osc-client-host> <osc-client-port>')
