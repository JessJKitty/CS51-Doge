
# given an array of sentences, break down into an array of 
# smaller sentences based on a heirarchy of divisors: 
# periods, semicolons, long and short dashes, colons, and
# at last resort, commas. This is to keep the runtime 
# manageble while not losing valuable relationship information
def split_sentence(sentenceArray):
	marks = [".", ";", "--", " - ", ":", ","]
	answer = sentenceArray
	for mark in marks:
		newAnswer = []
		for part in answer:
			if len(part) > 40:
				newAnswer += part.split(mark)
			else:
				newAnswer.append(part)
		answer = newAnswer
	# if string is too long and contains no divisors, split by space close to middle
	for sent in answer:
		if len(sent) > 40:
			space = sent.find(" ", len(sent)/2)
			sent2 = sent[:space]
			sent1 = sent[space:]
			ins = answer.index(sent)
			answer.remove(sent)
			answer.insert(ins, sent1)
			answer.insert(ins+1, sent2)
	return answer
