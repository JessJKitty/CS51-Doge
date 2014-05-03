import pickle

from collapse import collapse
from greedy import greedy
from Return_max import return_max
from Return_max import return_max_greed
from sentence_splitter import split_sentence

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

sentences = split_sentence(sentences)

answers = []
for aLine in answerLines:
	for answer in aLine:
		answers.append(answer)

generatedAnswers = []
greedyAnswers = []
START = 0
TOTAL = 40
count = 0
for line in sentences:
	count += 1
	if count < START:
		continue
	print line
	ans = return_max(collapse, line, words, combos)
	greedyans = return_max_greed(greedy, line, words, combos, possible)
	print ans
	print greedyans
	print "\n"

	for i in range(0, len(ans)):
		generatedAnswers.append(ans[i])
	for i in range(0, len(greedyans)):
		greedyAnswers.append(greedyans[i])

	if count > START + TOTAL:
		break

answersStart = 0
#answersStart = 0
#tick = 0
#for line in sentences:
#	tick += 1
#	for word in line:
#		answersStart += 1
#	if tick > START:
#		break

answers = filter(lambda a: a!='\n', answers)
answers = filter(lambda a: (any(c.isalpha() for c in a)), answers)
generatedAnswers = filter(lambda a: (any(c.isalpha() for c in a)), generatedAnswers)
greedyAnswers = filter(lambda a: (any(c.isalpha() for c in a)), greedyAnswers)
correct = 0
wrong = 0
for i in range(0, len(generatedAnswers)):
	if answers[answersStart:][i] == generatedAnswers[i]:
		correct += 1
	else:
		wrong += 1
greedyCorrect = 0
greedyWrong = 0
for i in range(0, len(greedyAnswers)):
	if answers[answersStart:][i] == greedyAnswers[i]:
		greedyCorrect += 1
	else:
		greedyWrong += 1


print "answers: " 
print answers[answersStart:answersStart+180]
print "generated: " 
print generatedAnswers
print "greedy: "
print greedyAnswers
print "c: " 
print correct
print "w: " 
print wrong
print "gc: " 
print greedyCorrect
print "gw: " 
print greedyWrong


