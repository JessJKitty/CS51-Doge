from __future__ import print_function
import itertools
from sentenceparsing import makelist

sentence = "Bear car seal miew?"

dict1 = { 
	"bear": {'NN': 0.8391, 'VB': 0.161921},
	"car": {'NN': 0.99999, 'VB': .000001},
        "seal": {'NN':1}
}

partset1 = ['NN', 'VB', 'MIEW', 'RAWR', 'WRATHKITTY']



def init_normalize(lis):
    #Take a list, and return a dictionary of the list elements
    #and a uniform distribution of probability
    l = len(lis)
    return {el: 1.0 / l for el in lis}
    
partdict1 = init_normalize(partset1)



def iterate(sentence, dictionary, partset):
    #Take all the words and look them up in the dictionary
    #if words are not in the dictionary, use default partset. 
    #Return the product of all the keys. 
    return itertools.product(*(dictionary.get(word, partset).keys() for word in makelist(sentence)))


#for i in iterate(sentence, dict1, partdict1): print(i)
