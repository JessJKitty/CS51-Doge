from __future__ import print_function
import pickle
from collapse import calc_base_prob
from Iteration import iterate
from Iteration import init_normalize
from sentenceparsing import makelist

# loads words dictionary with probabilities of parts of speech for each word
word_POS_freqs = pickle.load (open("words.p", "r"))

# loads combos dictionary with probabilities of parts of speech
# being following, given a certain part of speech
transition_probs = pickle.load (open("combos.p", "r"))

# takes out all the part of speech probabilities for the first word 
all_POS = pickle.load (open("pos.p", "r"))

# these are used to update the probabilities for the dictionary
transition_probs.update({('', '') : 1})
transition_probs.update({('', pos) : 1 for pos in all_POS})
transition_probs.update({(pos, '') : 1 for pos in all_POS})

# determines probability of part of speech sequence, based only on the most probable
# part of speech for each word. It does not take into account the probability of 
# combinations of part of speech
def greedy (sentence, word_POS_freqs, transition_probs, all_POS):
	# access base frequencies for all parts of speech
    POS_basefreqs = init_normalize(all_POS)
	# converts sentence into a list of words
    sen_list = makelist(sentence)
	# determine combinations of possible part of speech sequences
    POS_combinations = iterate(sentence, word_POS_freqs, POS_basefreqs)
	# returns dictionary with keys being possible part of speech 
	# sequences paired up with their respective probabilities
    return {POS_combo: calc_base_prob(sen_list, POS_combo, word_POS_freqs)
               for POS_combo in POS_combinations}