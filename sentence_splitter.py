

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

test = ["blah help testing yay for data this is so terrible why run time so bad doge why why why ugh no fair"]
print split_sentence(test)