import torchtext
import re
from torchtext import data
from torchtext import vocab

import torch
import torch.nn as nn
import torch.functional as F
import torch.nn.functional as F
from torch.autograd import Variable
import pandas as pd
import numpy as np
import torch.optim as optim

from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
from sklearn.model_selection import StratifiedShuffleSplit, train_test_split
from sklearn.metrics import accuracy_score
from tqdm import tqdm, tqdm_notebook, tnrange

import math
from getNews import getNews

tqdm.pandas(desc='Progress')

class BatchGenerator:
    def __init__(self, dl, x_field, y_field):
        self.dl, self.x_field, self.y_field = dl, x_field, y_field
        
    def __len__(self):
        return len(self.dl)
    
    def __iter__(self):
        for batch in self.dl:
            X = getattr(batch, self.x_field)
            y = getattr(batch, self.y_field)
            yield (X,y)

def tokenizer(s): 
    return [w.lower() for w in tweet_clean(s)]

def tweet_clean(text):
    text = re.sub(r'[^A-Za-z0-9]+', ' ', text) # remove non alphanumeric character
    text = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+','',text)
    return text.strip()

def CreateTrainDS(valid):
    result = pd.DataFrame()
    fields = ['Article','Label']
    file_dict = {'Altcoin':'newsAltcoin.tsv','Binance':'newsBinance.tsv','Bitcoin':'newsBitcoin.tsv','Blockchain':'newsBlockchain.tsv','CoinBase':'newsCoinBase.tsv','Ethereum':'newsEth.tsv','ICO':'newsICO.tsv','Litecoin':'newsLitecoin.tsv','Mining':'newsMining.tsv','Poloniex':'newsPoloniex.tsv','Satoshi':'newsSatoshi.tsv','Wallet':'newsWallet.tsv'}
    valid_file = "/home/nithin/Git/Cryptic/SentimentAnalysis/News/TSV/"+valid+"NewsValid.tsv"
    train_file = "/home/nithin/Git/Cryptic/SentimentAnalysis/News/TSV/NewsTrain.tsv"
    return train_file, valid_file

txt_field = data.Field(sequential=True, 
                       # tokenize=tokenizer, 
                       include_lengths=True, 
                       use_vocab=True)
label_field = data.Field(sequential=False, 
                             use_vocab=False, 
                             pad_token=None, 
                             unk_token=None)

def DefValid(train_File,valid_File):
    train_val_fields = [
        ('Article', txt_field), # process it as text
        ('Label', label_field) # process it as label
    ]
    trainds,valds = data.TabularDataset.splits(path='/home/nithin/Git/Cryptic/SentimentAnalysis/News/TSV', 
                                            format='tsv',  
                                            train=train_File,
                                            validation=valid_File, 
                                            fields=train_val_fields, 
skip_header=True)
    return trainds,valds

def NewsSentimentAnalysis(currency):
    getNews(currency)
    
    valid = currency 
    train_file,valid_file = CreateTrainDS(valid)
    trainds,valds = DefValid(train_file,valid_file)
    vec = vocab.Vectors('glove.twitter.27B.100d.txt', '/home/nithin/Git/Cryptic/GloVe-1.2')
    txt_field.build_vocab(trainds,valds, max_size=200000, vectors=vec)
    label_field.build_vocab(trainds)
    traindl,valdl = data.BucketIterator.splits(datasets=(trainds,valds), 
                                            batch_sizes=(512,1024), 
                                            sort_key=lambda x: len(x.Article),  
                                            sort_within_batch=True, 
                                            repeat=False)
    train_batch_it = BatchGenerator(traindl, 'Article', 'Label') # use the wrapper to convert Batch to data
    val_batch_it = BatchGenerator(valdl, 'Article', 'Label')
    
    vocab_size = len(txt_field.vocab)
    embedding_dim = 100
    n_hidden = 64
    n_out = 3

    model = ConcatPoolingGRUAdaptive(vocab_size, embedding_dim, n_hidden, n_out, valds.fields['Article'].vocab.vectors)
    # model.load_state_dict(torch.load("/home/nithin/Git/Cryptic/SentimentAnalysis/News/Models/NewsM1.pt"))
    # model.eval()
    opt = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), 1e-3)

    return fit(model, train_dl = train_batch_it, val_dl=val_batch_it, loss_fn=F.nll_loss, opt=opt, epochs=16)

class SimpleGRU(nn.Module):
    def __init__(self, vocab_size, embedding_dim, n_hidden, n_out, pretrained_vec, bidirectional=True):
        super().__init__()
        self.vocab_size,self.embedding_dim,self.n_hidden,self.n_out,self.bidirectional = vocab_size, embedding_dim, n_hidden, n_out, bidirectional
        self.emb = nn.Embedding(self.vocab_size, self.embedding_dim)
        self.emb.weight.data.copy_(pretrained_vec)
        self.emb.weight.requires_grad = False
        self.gru = nn.GRU(self.embedding_dim, self.n_hidden, bidirectional=bidirectional)
        self.out = nn.Linear(self.n_hidden, self.n_out)
        
    def forward(self, seq, lengths):
        bs = seq.size(1) # batch size
        seq = seq.transpose(0,1)
        self.h = self.init_hidden(bs) # initialize hidden state of GRU
        embs = self.emb(seq)
        embs = embs.transpose(0,1)
        embs = pack_padded_sequence(embs, lengths) # unpad
        gru_out, self.h = self.gru(embs, self.h) # gru returns hidden state of all timesteps as well as hidden state at last timestep
        gru_out, lengths = pad_packed_sequence(gru_out) # pad the sequence to the max length in the batch
        # since it is as classification problem, we will grab the last hidden state
        outp = self.out(self.h[-1]) # self.h[-1] contains hidden state of last timestep
        return F.log_softmax(outp)
    
    def init_hidden(self, batch_size): 
        if self.bidirectional:
            return torch.zeros((2,batch_size,self.n_hidden))
        else:
            return torch.zeros((1,batch_size,self.n_hidden))

class ConcatPoolingGRUAdaptive(nn.Module):
    def __init__(self, vocab_size, embedding_dim, n_hidden, n_out, pretrained_vec, bidirectional=True):
        super().__init__()
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.n_hidden = n_hidden
        self.n_out = n_out
        self.bidirectional = bidirectional
        
        self.emb = nn.Embedding(self.vocab_size, self.embedding_dim)
        self.emb.weight.data.copy_(pretrained_vec) # load pretrained vectors
        self.emb.weight.requires_grad = False # make embedding non trainable
        self.gru = nn.GRU(self.embedding_dim, self.n_hidden, bidirectional=bidirectional)
        if bidirectional:
            self.out = nn.Linear(self.n_hidden*2*2, self.n_out)
        else:
            self.out = nn.Linear(self.n_hidden*2, self.n_out)
        
    def forward(self, seq, lengths):
        bs = seq.size(1)
        self.h = self.init_hidden(bs)
        seq = seq.transpose(0,1)
        embs = self.emb(seq)
        embs = embs.transpose(0,1)
        embs = pack_padded_sequence(embs, lengths)
        gru_out, self.h = self.gru(embs, self.h)
        gru_out, lengths = pad_packed_sequence(gru_out)        
        
        avg_pool = F.adaptive_avg_pool1d(gru_out.permute(1,2,0),1).view(bs,-1)
        max_pool = F.adaptive_max_pool1d(gru_out.permute(1,2,0),1).view(bs,-1)        
        outp = self.out(torch.cat([avg_pool,max_pool],dim=1))
        return F.log_softmax(outp, dim=-1)
    
    def init_hidden(self, batch_size): 
        if self.bidirectional:
            return torch.zeros((2,batch_size,self.n_hidden))
        else:
            return torch.zeros((1,batch_size,self.n_hidden))

def fit(model, train_dl, val_dl, loss_fn, opt, epochs=3):
    num_batch = len(train_dl)
    senti_dict = {}
            
    for epoch in range(epochs):      
        y_true_train = list()
        y_pred_train = list()
        total_loss_train = 0          
        
        t = iter(train_dl)
        for (X,lengths),y in t:
            lengths = lengths.cpu().numpy()
                
            opt.zero_grad()
            pred = model(X, lengths)
            loss = loss_fn(pred, y)
            loss.backward()
            opt.step()
            
            pred_idx = torch.max(pred, dim=1)[1]
            
            y_true_train += list(y.cpu().data.numpy())
            y_pred_train += list(pred_idx.cpu().data.numpy())
            total_loss_train += loss.item()
            
        train_acc = accuracy_score(y_true_train, y_pred_train)
        train_loss = total_loss_train/len(train_dl)

    y_true_val = list()
    y_pred_val = list()
    total_loss_val = 0
    for (X,lengths),y in val_dl:
        pred = model(X, lengths.cpu().numpy())
        loss = loss_fn(pred, y)
        pred_idx = torch.max(pred, 1)[1]
        y_true_val += list(y.cpu().data.numpy())
        y_pred_val += list(pred_idx.cpu().data.numpy())
        total_loss_val += loss.item()
    valacc = accuracy_score(y_true_val, y_pred_val)
    valloss = total_loss_val/len(val_dl)
    y4senti = [i for i in y_pred_val if i!=1]
    avg_senti = np.mean(y4senti)
    
    if(math.isnan(avg_senti)):
        avg_senti = 1.0
    senti_dict[valacc] = avg_senti
    if(avg_senti<1.0):
            final_senti = 0 + ((avg_senti)/2)*100
    elif(avg_senti==1.0):
        final_senti = 50
    else:
        final_senti = 50 + ((avg_senti-1)/2)*100
    return final_senti

# getNews('XRP')

# finalSentiment = NewsSentimentAnalysis("XRP")
# print(finalSentiment)
