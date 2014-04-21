
# enter file names in Brown corpus in this array
fileNames = []

# file name constructor
fileNameDict = {"ca": 44, "cb": 27, "cc": 17, "cd": 17, "ce": 36, "cf": 48, "cg": 75, "ch": 30, "cj": 80, "ck": 29, "cl": 24, "cm": 06, "cn": 29, "cp": 29, "cr": 09}
for key in fileNameDict:
	for i in range(0, fileNameDict[key]):
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
	with open("brown/" + fileNames[i]) as file:
		for line in file:
			if line == "":
				continue
		    else:
		    	prevSpeech = ""
		    	lineArray = split(line, " ")
		    	for wordBlock in lineArray:
		    		slashIndex = wordBlock.find("/")
		    		word = wordBlock[:slashIndex]
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


