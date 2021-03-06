import pickle
from Iteration import iterate
from Iteration import init_normalize
from sentenceparsing import makelist

all_POS = pickle.load (open("pos.p", "r"))
POS_basefreqs = init_normalize(all_POS)


word_POS_freqs = pickle.load (open("words.p", "r"))
transition_probs = pickle.load (open("combos.p", "r"))

sentence = "I like cake"


def product(iterable):
    import operator
    return reduce(operator.mul, iterable, 1)

def calc_transition_prob(POS_list, transition_probs):
    return product(transition_probs.get((POS_list[i], POS_list[i+1]), 1)
                for i in range(len(POS_list) - 1))

def calc_base_prob(word_list, POS_list, word_POS_freqs):
    return product(word_POS_freqs.get(word, POS_basefreqs)[POS]
                for word, POS in zip(word_list, POS_list))

def collapse (sentence, word_POS_freqs, transition_probs):
    sen_list = makelist(sentence)
    print (sen_list)
    POS_combinations = list(iterate(sentence, word_POS_freqs, POS_basefreqs))
    numbers = [(calc_transition_prob(POS_combo, transition_probs)
                        * calc_base_prob(sen_list, POS_combo, word_POS_freqs))
               for POS_combo in POS_combinations]
    for i in range(min(len(list(POS_combinations)) -1, 100)): print(numbers[i])
    return dict(zip(POS_combinations, numbers))

#c = collapse(sentence, word_POS_freqs, transition_probs)
#print (max((c[x], x) for x in c)[1])

#print iterate(sentence, word_POS_freqs, all_POS)
