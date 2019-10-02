import numpy as np
import os
import json
import random
import torch
import torch.nn as nn
from torch import Tensor
from urllib.request import urlopen  # Py3

from IPython.core.display import display, HTML



def one_hot(p, dim):
    o=np.zeros(p.shape+(dim,), dtype=int)
    for y in range(p.shape[0]):
        for x in range(p.shape[1]):
            o[y,x,p[y,x]]=1
    return o

class TextLibrary:
    """
    TextLibrary class: text library for training, encoding, batch generation,
    and formatted source display.
    """
    def __init__(self, descriptors, max=100000000):
        self.descriptors=descriptors
        self.data=''
        self.files=[]
        self.c2i = {}
        self.i2c = {}
        index = 1
        for descriptor in descriptors:
            fd={}
            if descriptor[:4] == 'http':
                try:
                    dat = urlopen(descriptor).read().decode('utf-8')
                    self.data += dat
                    fd["name"] = descriptor
                    fd["data"] = dat
                    fd["index"] = index
                    index += 1
                    self.files.append(fd)
                except Exception as e:
                    print(f"Can't download {descriptor}: {e}")
            else:
                fd["name"] = os.path.splitext(os.path.basename(descriptor))[0]
                try:
                    f = open(descriptor)
                    dat = f.read(max)
                    self.data += dat
                    fd["data"] = dat
                    fd["index"] = index
                    index += 1
                    self.files.append(fd)
                    f.close()
                except Exception as e:
                    print(f"ERROR: Cannot read: {filename}: {e}")
        ind = 0
        for c in self.data:  # sets are not deterministic
            if c not in self.c2i:
                self.c2i[c] = ind
                self.i2c[ind] = c
                ind += 1
        self.ptr = 0
            
    def print_colored_IPython(self, textlist, pre='', post=''):
        bgcolors = ['#d4e6f1', '#d8daef', '#ebdef0', '#eadbd8', '#e2d7d5', '#edebd0',
                    '#ecf3cf', '#d4efdf', '#d0ece7', '#d6eaf8', '#d4e6f1', '#d6dbdf',
                    '#f6ddcc', '#fae5d3', '#fdebd0', '#e5e8e8', '#eaeded', '#A9CCE3']
        out = ''
        for txt, ind in textlist:
            txt = txt.replace('\n','<br>')
            if ind==0:
                out += txt
            else:
                out += "<span style=\"background-color:"+bgcolors[ind%16]+";\">" + txt +\
                       "</span>"+"<sup>[" + str(ind) + "]</sup>"
        display(HTML(pre+out+post))
        
    def source_highlight(self, txt, minQuoteSize=10):
        tx = txt
        out = []
        qts = []
        txsrc=[("Sources: ", 0)]
        sc=False
        noquote = ''
        while len(tx)>0:  # search all library files for quote 'txt'
            mxQ = 0
            mxI = 0
            mxN = ''
            found = False
            for f in self.files:  # find longest quote in all texts
                p = minQuoteSize
                if p<=len(tx) and tx[:p] in f["data"]:
                    p = minQuoteSize + 1
                    while p<=len(tx) and tx[:p] in f["data"]:
                        p += 1
                    if p-1>mxQ:
                        mxQ = p-1
                        mxI = f["index"]
                        mxN = f["name"]
                        found = True
            if found:  # save longest quote for colorizing
                if len(noquote)>0:
                    out.append((noquote, 0))
                    noquote = ''
                out.append((tx[:mxQ],mxI))
                tx = tx[mxQ:]
                if mxI not in qts:  # create a new reference, if first occurence
                    qts.append(mxI)
                    if sc:
                        txsrc.append((", ", 0))
                    sc = True
                    txsrc.append((mxN,mxI))
            else:
                noquote += tx[0]
                tx = tx[1:]
        if len(noquote)>0:
            out.append((noquote, 0))
            noquote = ''
        self.print_colored_IPython(out)
        if len(qts)>0:  # print references, if there is at least one source
            self.print_colored_IPython(txsrc, pre="<small><p style=\"text-align:right;\">",
                                     post="</p></small>")
    
    def get_slice(self, length):
        if (self.ptr + length >= len(self.data)):
            self.ptr = 0
        if self.ptr == 0:
            rewind = True
        else:
            rewind = False
        sl = self.data[self.ptr:self.ptr+length]
        self.ptr += length
        return sl, rewind
    
    def decode(self, ar):
         return ''.join([self.i2c[ic] for ic in ar])
            
    def get_random_slice(self, length):
        p = random.randrange(0,len(self.data)-length)
        sl = self.data[p:p+length]
        return sl
    
    def get_slice_array(self, length):
        ar = np.array([c for c in self.get_slice(length)[0]],dtype=int)
        return ar
        
    def get_sample(self, length):
        s, rewind = self.get_slice(length+1)
        X = np.array([self.c2i[c] for c in s[:-1]],dtype=int)
        y = np.array([self.c2i[c] for c in s[1:]],dtype=int)
        return (X, y, rewind)
    
    def get_random_sample(self, length):
        s = self.get_random_slice(length+1)
        X = np.array([self.c2i[c] for c in s[:-1]],dtype=int)
        y = np.array([self.c2i[c] for c in s[1:]],dtype=int)
        return (X, y)
    
    def get_sample_batch(self, batch_size, length):
        smpX = np.zeros((batch_size,length),dtype=int)
        smpy = np.zeros((batch_size,length),dtype=int)
        for i in range(batch_size):
            smpX[i,:], smpy[i,:], _ = self.get_sample(length)
        return smpX, smpy
        
    def get_random_sample_batch(self, batch_size, length):
        smpX = np.zeros((batch_size,length),dtype=int)
        smpy = np.zeros((batch_size,length),dtype=int)
        for i in range(batch_size):
            smpX[i,:], smpy[i,:] = self.get_random_sample(length)
        return smpX, smpy
    
    
class Poet(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, device):
        super(Poet, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_size = output_size
        self.device=device
        
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size, num_layers=num_layers, batch_first=True, dropout=0)
        
        self.demb = nn.Linear(hidden_size, output_size)
        self.softmax = nn.Softmax(dim=-1)  # negative dims are a recent thing (as 2018-03), remove for old vers.
    
    def init_hidden(self, batch_size):
        self.h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size, device=self.device)
        self.c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size, device=self.device)

    def forward(self, inputx, steps):
        self.lstm.flatten_parameters()
        hn, (self.h0, self.c0) = self.lstm(inputx.to(self.device), (self.h0, self.c0))
        hnr = hn.contiguous().view(-1,self.hidden_size)
        op = self.demb(hnr)
        opr = op.view(-1, steps ,self.output_size)
        return opr

    def generate(self, n, textlib, start=None):
        s=''
        torch.set_grad_enabled(False)
        if start==None or len(start)==0:
            start=' '
        self.init_hidden(1)
        for c in start:
            X=np.array([[textlib.c2i[c]]])
            Xo=one_hot(X,self.output_size)
            Xt = Tensor(torch.from_numpy(np.array(Xo,dtype=np.float32))).to(self.device)
            ypl = self.forward(Xt,1)
            ypl2 = ypl.view(-1,self.output_size)
            yp = self.softmax(ypl2)
        for i in range(n):
            ypc=Tensor.cpu(yp.detach()) # .cpu()
            y_pred=ypc.numpy()
            inds=list(range(self.output_size))
            ind = np.random.choice(inds, p=y_pred.ravel())
            s=s+textlib.i2c[ind]
            X=np.array([[ind]])
            Xo=one_hot(X,self.output_size)
            Xt = Tensor(torch.from_numpy(np.array(Xo,dtype=np.float32))).to(self.device)
            ypl = self.forward(Xt,1)
            ypl2 = ypl.view(-1,self.output_size)
            yp = self.softmax(ypl2)
        torch.set_grad_enabled(True)
        return s
