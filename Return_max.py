from __future__ import print_function
import pickle
from greedy import greedy
from collapse import collapse


##def return_max (function, sentence, word_POS_freqs, transition_probs):
##    c = function(sentence, word_POS_freqs, transition_probs)
##    try:
##        return max([(c[x], x) for x in c])[1]
##    except: return "miew. errors!"


def return_max (function, sentence, word_POS_freqs, transition_probs):
    c = function(sentence, word_POS_freqs, transition_probs)
    return (max(c, key=lambda x: c[x]))

def return_max_greed (function, sentence, word_POS_freqs, transition_probs, all_probs):
    c = function(sentence, word_POS_freqs, transition_probs, all_probs)
    return (max(c, key=lambda x: c[x]))
