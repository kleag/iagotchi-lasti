import os
import torch
import collections
import random


class Dictionary(object):

    def __init__(self):
        self.word2idx = {'<unk>': 0}
        self.idx2word = ['<unk>']
        self.frequency = collections.defaultdict(int)

    def add_word(self, word):
        if word not in self.word2idx:
            self.idx2word.append(word)
            self.word2idx[word] = len(self.idx2word) - 1
        self.frequency[word] += 1
        return self.word2idx[word]

    def min_frequency(self, value):
        self.idx2word = filter(lambda word: self.frequency[word] >= value or word in ['<unk>'], self.idx2word)
        self.word2idx = {word: i for i, word in enumerate(self.idx2word)}

    def __len__(self):
        return len(list(self.idx2word))


def shuffle_on_symbol(ids, symbol):
    sequences = []
    sequence = []
    for i, element in enumerate(ids):
        sequence.append(element)
        if element == symbol and len(sequence) > 0:
            sequences.append(sequence)
            sequence = []
    if len(sequence) > 0:
        sequences.append(sequence)
    random.shuffle(sequences)
    return torch.LongTensor(reduce(lambda x, y: x + y, sequences))


class Corpus(object):

    def __init__(self, path, min_frequency=0, add_eos=True):
        self.dictionary = Dictionary()
        print('loading train.txt')
        self.train = self.tokenize(os.path.join(path, 'train.txt'), training=True, min_frequency=min_frequency, add_eos=add_eos)
        print('loading valid.txt')
        self.valid = self.tokenize(os.path.join(path, 'valid.txt'), add_eos=add_eos)
        print('loading test.txt')
        self.test = self.tokenize(os.path.join(path, 'test.txt'), add_eos=add_eos)

    def tokenize(self, path, training=False, min_frequency=0, add_eos=True):
        """
        Tokenizes a text file.
        """
        assert os.path.exists(path)
        # Add words to the dictionary
        with open(path, 'r') as f:
            tokens = 0
            for line in f:
                words = line.split() + (['<eos>'] if add_eos else [])
                tokens += len(words)
                if training:
                    for word in words:
                        self.dictionary.add_word(word)

        self.dictionary.min_frequency(min_frequency)
        # Tokenize file content
        with open(path, 'r') as f:
            ids = torch.LongTensor(tokens)
            token = 0
            for line in f:
                words = line.split() + (['<eos>'] if add_eos else [])
                for word in words:
                    if word in self.dictionary.word2idx:
                        ids[token] = self.dictionary.word2idx[word]
                    else:
                        ids[token] = 0
                    token += 1

        return ids
