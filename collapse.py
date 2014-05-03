from __future__ import print_function
import pickle
from Iteration import iterate
from Iteration import init_normalize
from sentenceparsing import makelist

# takes out all the part of speech probabilities for the first word 
all_POS = pickle.load (open("pos.p", "r"))
POS_basefreqs = init_normalize(all_POS)

# loads words dictionary with probabilities of parts of speech for each word
word_POS_freqs = pickle.load (open("words.p", "r"))

# loads combos dictionary with probabilities of parts of speech
# being following, given a certain part of speech
transition_probs = pickle.load (open("combos.p", "r"))

# This should be added to the basic transition_probs dictionary source
transition_probs.update({('', '') : 1})
transition_probs.update({('', pos) : 1 for pos in all_POS})
transition_probs.update({(pos, '') : 1 for pos in all_POS})


def product(iterable):
    import operator
    return reduce(operator.mul, iterable, 1)

# calculates probabilities of each combo in a part of speech list
# for example, for a sequence "n"-"v"-"n", we calculate the product of
# the probabilities of "n"-"v" and "v"-"n" and returns the value
def calc_transition_prob(POS_list, transition_probs):
    return product(transition_probs.get((POS_list[i], POS_list[i+1]), 1)
                for i in range(len(POS_list) - 1))

# calculates probabilities of a list of words being specific parts of speech
# for example, for list ["I", "am"] and sequence "pn"-"v", we calculate the 
# product of the probability of "I" being a pronoun and "am" being a verb
def calc_base_prob(word_list, POS_list, word_POS_freqs):
    return product(word_POS_freqs.get(word, POS_basefreqs)[POS]
                for word, POS in zip(word_list, POS_list))

# given a sentence, returns dictionary with part of speech sequences with its corresponding probability
def collapse (sentence, word_POS_freqs, transition_probs):
	# creates list of words from sentence
    sen_list = makelist(sentence)
	# creates list of tuples of potential part of speech sequences
    POS_combinations = iterate(sentence, word_POS_freqs, POS_basefreqs)
	# calculates probabilities for each possible sequence and returns probabilities in a dictionary
    return {POS_combo: (calc_transition_prob(POS_combo, transition_probs)
                        * calc_base_prob(sen_list, POS_combo, word_POS_freqs))
               for POS_combo in POS_combinations}

##def return_max (function, sentence, word_POS_freqs, transition_probs):
##    c = function(sentence, word_POS_freqs, transition_probs)
##    return (max(c, key=lambda x: c[x]))
##
##print (return_max(collapse, sentence, word_POS_freqs, transition_probs))

#c = collapse(sentence, word_POS_freqs, transition_probs)
#print (max(c, key=lambda x: c[x]))

#print iterate(sentence, word_POS_freqs, all_POS)
