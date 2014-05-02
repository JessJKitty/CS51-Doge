import pickle

from collapse import collapse
from Return_max import return_max

words = pickle.load(open("words.p", "rb"))
combos = pickle.load(open("combos.p", "rb"))
possible = pickle.load(open("pos.p", "rb"))


# enter file names in Brown corpus in this array
fileNames = []

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

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

toTestLines = []
answerLines = []

for i in fileNames:
	with open("brown/" + i) as file:
		for line in file:
			if line != "":
				lineArray = line.split(" ")
				speechArray = []
				wordsArray = []
				for wordBlock in lineArray:
					slashIndex = wordBlock.find("/")
					dashIndex = wordBlock.find("-")
					word = wordBlock[:slashIndex].lower()
					wordsArray.append(word)
					if dashIndex > 0:
						speech = wordBlock[slashIndex+1:dashIndex]
					else:
						speech = wordBlock[slashIndex+1:]
					if speech.find("/") > 0:
						speech = speech[speech.find("/")+1:]
					if hasNumbers(speech) or (speech.find("/") > 0):
						speech = "ok error"
					speechArray.append(speech)
				toTestLines.append(wordsArray)
				answerLines.append(speechArray)

# convert lines array of word arrays to array of sentences
sentences = []
for line in toTestLines:
	stringLine = ""
	for word in line:
		stringLine = stringLine + word + " "
	sentences.append(stringLine)

count = 0
for line in sentences:
	print line
	print return_max(collapse, line, words, combos)
	print "\n"
	count +=1
	if count > 20:
		break



