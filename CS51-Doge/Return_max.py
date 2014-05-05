import pickle
from greedy import greedy
from collapse import collapse


def return_max (function, sentence, word_POS_freqs, transition_probs):
    c = function(sentence, word_POS_freqs, transition_probs)
    try:
	return max([(c[x], x) for x in c])[1]
    except: return "miew. errors!"
