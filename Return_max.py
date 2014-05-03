from __future__ import print_function
import pickle
from greedy import greedy
from collapse import collapse


def return_max (function, sentence, word_POS_freqs, transition_probs):
    # call the function on the other args, then return the key
    # that corresponds to the max value in the dict. 
    c = function(sentence, word_POS_freqs, transition_probs)
    return (max(c, key=lambda x: c[x]))

def return_max_greed (function, sentence, word_POS_freqs, transition_probs, all_probs):
    c = function(sentence, word_POS_freqs, transition_probs, all_probs)
    return (max(c, key=lambda x: c[x]))
