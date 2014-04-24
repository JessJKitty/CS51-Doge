from __future__ import print_function

sentence = ["bear", "car", "seal"]

dict1 = { 
	"bear": {'NN': 0.8391, 'VB': 0.171921},
	"car": {'NN': 0.99999, 'VB': .000001},
        "seal": {'NN':1}
}

def iterate(sentence, dictionary):
    finallist = [""] 
    for i in sentence:
        currlist = list(finallist)
        newlist = []
        for j in dictionary[i].keys():
            for k in currlist:
                newlist.append(k + ">" + j)
        finallist = list(newlist)
    return [x.lstrip(">") for x in finallist]
            

print (iterate(sentence, dict1))
