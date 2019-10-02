

from TextGenerator import TextLibrary, Poet
import os, json
import torch.nn as nn
import torch
import numpy as np
from torch import Tensor





class TextGeneratorTraining(object):
    
    def __init__(self):
        self.libfile = 'lib.json'
        
        self.libdesc = self.getLib()
        self.textlib = TextLibrary(self.libdesc["lib"])
        model_params_lib = {
            "model_name": "lib",
            "vocab_size": len(self.textlib.i2c),
            "neurons": 512,
            "layers": 4,
            "learning_rate": 2.e-4,
            "steps": 80,
            "batch_size": 128
        }
        self.model_params = model_params_lib

    def getLib(self):
        libdesc = None
        if os.path.exists(self.libfile):
            with open(self.libfile, 'r') as lib_file:
                libdesc = json.load(lib_file)
                
        return libdesc
    
    def one_hot(self, p, dim):
        o=np.zeros(p.shape+(dim,), dtype=int)
        for y in range(p.shape[0]):
            for x in range(p.shape[1]):
                o[y,x,p[y,x]]=1
        return o

    def get_data(self, batch_size, steps, vocab_size, device):
        X, y=self.textlib.get_random_sample_batch(batch_size, steps)
        Xo = self.one_hot(X, vocab_size)
        
        # Xt = Tensor(torch.from_numpy(np.array(Xo,dtype=np.float32)), requires_grad=False, dtype=torch.float32, device=device)
        # yt = Tensor(torch.from_numpy(y), requires_grad=False, dtype=torch.int32, device=device)
        Xt = Tensor(torch.from_numpy(np.array(Xo,dtype=np.float32))).to(device)
        Xt.requires_grad_(False)
        yt = torch.LongTensor(torch.from_numpy(np.array(y,dtype=np.int64))).to(device)
        yt.requires_grad_(False)
        return Xt, yt
    
    def training(self, force_cpu=False):
        batch_size = self.model_params['batch_size']
        vocab_size = self.model_params['vocab_size']
        steps = self.model_params['steps']
        print('model_params {}'.format(self.model_params))
        if torch.cuda.is_available() and force_cpu is not True:
            device='cuda'
            use_cuda = True
            print("Running on GPU")
        else:
            device='cpu'
            use_cuda = False
            print("Running on CPU")
            print("Note: on Google Colab, make sure to select:")
            print("      Runtime / Change Runtime Type / Hardware accelerator: GPU")
            
        poet = Poet(vocab_size, self.model_params['neurons'], self.model_params['layers'], vocab_size, device).to(device)
        
        ls=0
        nrls=0
        if use_cuda:
            intv=250
        else:
            intv=10
        for e in range(2500000):
            Xt, yt = self.get_data(batch_size, steps, vocab_size, device)
            if (e+1)%intv==0:
                l,pr=self.train(Xt,yt, poet, steps, vocab_size, True)
            else:
                l,pr=self.train(Xt,yt,poet, steps, vocab_size, False)        
            ls=ls+l
            nrls=nrls+1
            if (e+1)%intv==0:
                print("Loss: {} Precision: {}".format(ls/nrls, pr))
                # if use_cuda:
                #    print("Memory allocated: {} max_alloc: {} cached: {} max_cached: {}".format(torch.cuda.memory_allocated(), torch.cuda.max_memory_allocated(), torch.cuda.memory_cached(), torch.cuda.max_memory_cached()))
                nrls=0
                ls=0
                tgen=poet.generate(200, self.textlib, "\n\n")
                self.textlib.source_highlight(tgen,10)
        
    def train(self, Xt, yt, poet, steps, vocab_size, bPr=False):
        criterion = nn.CrossEntropyLoss()
        learning_rate = self.model_params['learning_rate']

        opti = torch.optim.Adam(poet.parameters(),lr=learning_rate);

        bok=0
        poet.zero_grad()

        poet.init_hidden(Xt.size(0))
        output = poet(Xt, steps)
        
        olin=output.view(-1,vocab_size)
        _, ytp=torch.max(olin,1)
        ytlin=yt.view(-1)

        pr=0.0
        if bPr: # Calculate precision
            ok=0
            nok=0
            for i in range(ytlin.size()[0]):
                i1=ytlin[i].item()
                i2=ytp[i].item()
                if i1==i2:
                    ok = ok + 1
                else:
                    nok = nok+1
                pr=ok/(ok+nok)
                
        loss = criterion(olin, ytlin)
        ls = loss.item()
        loss.backward()
        opti.step()

        return ls, pr

#print(libdesc)


#print(textlib.c2i)

gentrain = TextGeneratorTraining()
gentrain.training(force_cpu=True)







