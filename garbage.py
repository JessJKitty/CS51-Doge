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
