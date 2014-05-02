

def split_sentence(sentence):
	marks = [".", ";", "--", " - ", ":", ","]
	answer = [sentence]
	for mark in marks:
		newAnswer = []
		for part in answer:
			if len(part) > 60:
				newAnswer += part.split(mark)
			else:
				newAnswer.append(part)
		answer = newAnswer
	return answer