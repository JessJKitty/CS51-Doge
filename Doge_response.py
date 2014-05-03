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
    #tokenize sentence
    sen_list = makelist(sentence)
    
    #find the tuple that we think corresponds to the true POS
    c = return_max(collapse, sentence, word_POS_freqs, transition_probs)

    #define parts we want to look at
    important = {'nn', 'nn$', 'nnS' ,'nns$', 'np', 'np$', 'nps', 'nps$', 'nr'}
    others = {'jj', 'jjr', 'jjs', 'jjt'}

    #define the things that Doge says
    stockphrases = [" Such ", " Very ", " Many ", " Wow ", " OMG ", " how to "]

    #initialize keyphrase list
    say = []
    for i in range(len(c)):
        # if c[i] is an adjective, add it
        if c[i] in others:
            say.append(sen_list[i])

        # if c[i] is a noun, wiki it and add those things. 
        if c[i] in important:
            for j in wikiscraping(sen_list[i]):
                say.append(j)

    #pick something random in the list                
    def pickrand (list):
        return list[random.randint(0, len(list))]

    #generate an n - long doge phrase
    def generate (n, stock, say):
        response = ''
        for i in range(n):
            response += stock[random.randint(0, len(stock) - 1)] + say[random.randint(0, len(say) - 1)] + '.'
        response += " Amaze!"
        return response
                                                                   
    
    #max the doge phrase at 3, and if there are no key words, return "Wow, Amaze! Many brilliant"
    if len(say) == 0: return "Wow, Amaze! Many brilliant"
    else: return generate(min(3,len(say)), stockphrases, say)
    
doge_response("moo cow", word_POS_freqs, transition_probs)
