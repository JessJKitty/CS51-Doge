from __future__ import print_function
import pickle
from Iteration import iterate
from Iteration import init_normalize
from sentenceparsing import makelist
from collapse import collapse
from Return_max import return_max
from wikiscraping import wikiscraping
import random

all_POS = pickle.load (open("pos.p", "r"))
POS_basefreqs = init_normalize(all_POS)


word_POS_freqs = pickle.load (open("words.p", "r"))
transition_probs = pickle.load (open("combos.p", "r"))

# This should be added to the basic transition_probs dictionary source
transition_probs.update({('', '') : 1})
transition_probs.update({('', pos) : 1 for pos in all_POS})
transition_probs.update({(pos, '') : 1 for pos in all_POS})

def doge_response(sentence, word_POS_freqs, transition_probs):
    sen_list = makelist(sentence)
    c = return_max(collapse, sentence, word_POS_freqs, transition_probs)
    #for e in c: print(e)
    important = {'nn', 'nn$', 'nnS' ,'nns$', 'np', 'np$', 'nps', 'nps$', 'nr'}
    others = {'jj', 'jjr', 'jjs', 'jjt'}
    stockphrases = [" Such ", " Very ", " Many ", " Wow ", " OMG ", " how to "]
    say = []
    for i in range(len(c)):
        # print (i in important)
        if c[i] in others:
            say.append(sen_list[i])
            #print("checking")
        if c[i] in important:
            for j in wikiscraping(sen_list[i]):
                say.append(j)
            #print("checking")
                
    def pickrand (list):
        return list[random.randint(0, len(list))]

    def generate (n, stock, say):
        response = ''
        for i in range(n):
            response += stock[random.randint(0, len(stock) - 1)] + say[random.randint(0, len(say) - 1)] + '.'
        response += " Amaze!"
        return response
                                                                   
    
    
    if len(say) == 0: return "Wow, Amaze! Many brilliant"
    else: return generate(min(3,len(say)), stockphrases, say)
    
doge_response("moo cow", word_POS_freqs, transition_probs)
