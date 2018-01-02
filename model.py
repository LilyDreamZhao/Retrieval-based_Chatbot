#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 29 23:28:20 2017

@author: janinanu
"""

import torch
import torch.utils.data
import torch.autograd as autograd
import torch.nn as nn
from torch.nn import init
import torch.nn.functional as F
import torch.optim as optim
import torch.nn.utils.rnn 
import preprocess
#import data
#from torch.nn.utils.rnn import pad_sequence

#%%
#word = "<PAD>"
#
#embedding_size = vec_length
#
#vocab_len = len(vocab)
#
#embeds = nn.Embedding(vocab_len, embedding_size)
#
#lookup = torch.LongTensor([word_to_id[word+"\n"]])
#
#word_embed = embeds(autograd.Variable(lookup))
#
#print(word_embed)

#%% class

class Encoder(nn.Module):

    def __init__(self, input_size, hidden_size, vocab_size, num_layers = 1, dropout = 0, 
                 bidirectional = False): 
        super(Encoder, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.vocab_size = vocab_size
        self.num_layers = num_layers
        
        self.num_directions = 1
        
        self.embedding = nn.Embedding(vocab_size, input_size, spare = False,
                                      padding_idx = 0)
        self.lstm = nn.LSTM(input_size, self.hidden_size, num_layers = num_layers, batch_first=True,
                                   dropout = dropout, bidirectional=False, )
        
        self.init_weights()
        self.init_embedding()

    def init_weights(self):
        init.orthogonal(self.lstm.weight_ih_l0)
        init.uniform(self.lstm.weight_hh_l0, a=-0.01, b=0.01)
    
    def init_embedding(self):
             
        embedding_weights = torch.FloatTensor(self.vocab_size, self.input_size)
        #init.uniform(embedding_weights, a = -0.25, b= 0.25)
        
        word_to_id = preprocess.make_word_to_id('my_vocab.txt') 
        id_to_vec, embedding_dim = preprocess.make_id_to_vec('glove.6B.100d.txt', word_to_id)
        
        for id, vec in id_to_vec.items():
            embedding_weights[id] = vec 
        
        del self.embedding.weight
        self.embedding.weight.data.copy_(embedding_weights)
        
#%%
        
class DualEncoder(nn.Module):
     
    def __init__(self, encoder):
         super(DualEncoder, self).__init__()
         self.encoder = encoder
         self.number_of_layers = 2
         #h_0 (num_layers * num_directions, batch, hidden_size): 
         #tensor containing the initial hidden state for each element in the batch.
         dual_hidden_size = self.encoder.hidden_size * self.encoder.num_directions
         
         M = torch.FloatTensor(dual_hidden_size, dual_hidden_size)
         
         init.normal(M)
         
         self.M = nn.Parameter(M, requires_grad = True)

#%%

    def forward(self, contexts, responses):
        #output (seq_len, batch, hidden_size * num_directions): 
        #tensor containing the output features (h_t) from the last layer 
        #of the RNN, for each t. 
        
        #h_n (num_layers * num_directions, batch, hidden_size): 
        #tensor containing the hidden state for t=seq_len
        context_out, context_hn = self.encoder(contexts)
        context_hn = context_hn[0] #final hidden state in layer 0
        
        response_out, response_hn = self.encoder(responses)
        response_hn = response_hn[0]
        
        dual_hidden_size = self.encoder.hidden_size * self.encoder.num_directions
        

#%%
        
        scores_list = []
        
        for e in range(len(context_hn[0])): #context_hn = context_hn[0] #over all examples
            #context_out[e][-1].view(1, dual_hidden_size)
            context_h = context_out[-1][e].view(1, dual_hidden_size)#context_out[-1] = context_hn
            #spread hidden_size*num_directions over hidden_size*num_directions?
            
            response_h = response_out[-1][e].view(dual_hidden_size,1)
            #gives vectors of hidden_size for each example
#%%
                
#        dense_bilinear = nn.Bilinear(dual_hidden_size, dual_hidden_size, 1)
#        context_summary = context_hn #context.shape = batchsize x dual_hidden_size
#        response_summary = response_hn #response.shape = batchsize x dual_hidden_size
#        bilinear_output = dense_bilinear(context_summary, response_summary)
            
#        M = dense_bilinear.weight
#         
#        dense_sigmoid = nn.Sigmoid() #leave out if BCELossWithLogits() ?
#        sigmoid_input = bilinear_output # batch_size x 1
#        scores = dense_sigmoid(sigmoid_input) # batch_size x 1
            
            
           # dot = torch.mm(context_h, self.M), response_h))#gives 1x1 vector
         
            scalar = dot[0]
            
            prob = torch.sigmoid(scalar)
            
            scores.append(prob)
            
        scores = torch.stack(scores_list)
        
        return scores #to be used in training to compare with label
     
     

     
     
     
#%%
        
#m = nn.Bilinear(20, 30, 40)
#input1 = autograd.Variable(torch.randn(128, 20))
#input2 = autograd.Variable(torch.randn(128, 30))
#output = m(input1, input2)
#print(output.size())
        
#%%  
#m = nn.Sigmoid()
#input = autograd.Variable(torch.randn(2))
#print(input)
#print(m(input))      
     
     
     
     
     
     
     
     
        
