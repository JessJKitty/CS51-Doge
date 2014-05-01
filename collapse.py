import pickle
from Iteration import iterate
from sentenceparsing import makelist

words = pickle.load (open("words.p", "r"))
combos = pickle.load (open("combos.p", "r"))
pos = pickle.load (open("pos.p", "r"))


sentence = "My name is Kelwen"
sen_list = makelist(sentence)
print pos

#print iterate(sentence, words, pos)