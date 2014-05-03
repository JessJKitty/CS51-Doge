##def iterate(sentence, dictionary):
##    finallist = [""] 
##    for i in sentence:
##        currlist = list(finallist)
##        newlist = []
##        for j in dictionary[i].keys():
##            for k in currlist:
##                newlist.append(k + ">" + j)
##        finallist = list(newlist)
##    return [x.lstrip(">") for x in finallist]


## Just kidding lol. Python. We can do this much easier with the product thing from itertools. 

## Don't want to use this class:

##class ProbabilityDistribution(dict):
##    def __new__(self, normalized_dict):
##        return normalized_dict
##        
##    @staticmethod
##    def init_from_list(lis):
##        l = len(lis)
##        return ProbabilityDistribution({el: 1.0 / l for el in lis})
##
##    @staticmethod
##    def init_from_dict(dic):
##        total = sum(v for v in dic.values())
##        return ProbabilityDistribution({k: v / total for k,v in dic.items()})


## Kelwen is so stupid......
#def choose (dictionary):
#	keys = dictionary.keys()
#	best = keys[0]
#	for i in keys:
#		if dictionary[best] > dictionary [i]:
#	return best

# outputs list of possible sequences, given current part of speech
# def get_seq (pos):
#	seq_list = []
#	keys = combos.keys()
#	for seq in keys:
#		if seq[0] == pos:
#			seq_list.append(seq)
#	return seq_list
	
# finds list of probabilities of potential parts of speech for next word
# def find_probabilities (prev_pos, word):
#	if prev_pos == "START":
#		return words[word]
#	else:
#		probs = {}
#		seq_list = get_seq(prev_pos)
#		for seq in seq_list: 
#			try:
#				probs.append((seq[1],(combos[seq] * words[word][seq[1]])))
#			except:
#				pass
#		return probs		
#v = find_probabilities ('at', 'lounge')
#w = find_probabilities ('START', 'the')

#example = [[.34, 'n','v','n'], [.25, 'v','v','n']]
#def collapse (final_seqs, prob_list):
##	if len(final_seqs) == 0:
##		for prob in prob_list:
##			final_seqs.append([prob_list[prob], prob])
##	else:
##		for prob in prob_list:
##			for seq in final_seqs:
##				seq[0] *= prob[1]
##				seq.append(prob[0])
#answer = []
#s1 = find_probabilities('START', 'the')
#print s1
#collapse (answer, s1)
#print answer
#s2a = find_probabilities('at', 'word')
#s2b = find_probabilities('nil', 'word')
#print s2a
#print s2b

##def return_max (function, sentence, word_POS_freqs, transition_probs):
##    c = function(sentence, word_POS_freqs, transition_probs)
##    try:
##        return max([(c[x], x) for x in c])[1]
##    except: return "miew. errors!"






