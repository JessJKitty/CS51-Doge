import pickle

# enter file names in Brown corpus in this array
fileNames = []

# file name constructor
fileNameDict = {"ca": 44, "cb": 27, "cc": 17, "cd": 17, "ce": 36, "cf": 48, "cg": 75, "ch": 30, "cj": 80, "ck": 29, "cl": 24, "cm": 06, "cn": 29, "cp": 29, "cr": 9}
for key in fileNameDict:
	for i in range(1, fileNameDict[key]):
		if i < 10:
			istr = "0" + str(i)
		else:
			istr = str(i)
		name = key + istr
		fileNames.append(name)

# datastructure to store probabilites
### 2-pair probabilities
# single-layer dictionary
combos = {}

### Each word probability of different parts of speech
# Dictionary of dictionaries
words = {}

for i in fileNames:
	with open("brown/" + i) as file:
		for line in file:
			if line != "":
		    		prevSpeech = ""
		    	lineArray = line.split(" ")
		    	for wordBlock in lineArray:
		    		slashIndex = wordBlock.find("/")
		    		dashIndex = wordBlock.find("-")
		    		word = wordBlock[:slashIndex].lower()
		    		if dashIndex > 0:
		    			speech = wordBlock[slashIndex+1:dashIndex]
		    		else:
		    			speech = wordBlock[slashIndex+1:]
		    		# fill words dict
		    		if word not in words:
		    			words[word] = {speech: 1}
		    		else:
		    			if speech not in words[word]:
		    				words[word][speech] = 1
		    			else:
		    				words[word][speech] += 1
		    		# fill combos dict
		    		if prevSpeech == "":
		    			prevSpeech = speech
		    		else:
		    			speechPair = (prevSpeech, speech)
		    			if speechPair not in combos:
		    				combos[speechPair] = 1
		    			else:
		    				combos[speechPair] += 1

# generate decimal probabilities from totals
# combos
totals = {}
for pair in combos:
	first = pair[0]
	if first not in totals:
		totals[first] = combos[pair]
	else:
		totals[first] += combos[pair]
for pair in combos:
	first = pair[0]
	combos[pair] = combos[pair] / float(totals[first])
# words
for word in words:
	total = 0
	for speech in words[word]:
		total += words[word][speech]
	for speech in words[word]:
		words[word][speech] = words[word][speech] / float(total)

# export data
with open("words.p", "wb") as dataOut:
	pickle.dump(words, dataOut)

with open("combos.p", "wb") as dataOut:
	pickle.dump(combos, dataOut)



