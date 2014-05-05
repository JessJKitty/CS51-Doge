import pickle
from collapse import calc_base_prob
from Iteration import iterate
from Iteration import init_normalize
from sentenceparsing import makelist


word_POS_freqs = pickle.load (open("words.p", "r"))
transition_probs = pickle.load (open("combos.p", "r"))
all_POS = pickle.load (open("pos.p", "r"))

sentence = "The poop went down the street"

def greedy (sentence, word_POS_freqs, transition_probs, all_POS):
    POS_basefreqs = init_normalize(all_POS)
    sen_list = makelist(sentence)
    POS_combinations = iterate(sentence, word_POS_freqs, POS_basefreqs)
    return dict(zip(POS_combinations, [calc_base_prob(sen_list, POS_combo, word_POS_freqs)
               for POS_combo in POS_combinations]))

#c = greedy(sentence, word_POS_freqs, transition_probs, all_POS)
#print (max(c, key=lambda x: c[x]))
