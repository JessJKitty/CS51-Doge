from __future__ import print_function

# potential punctuations to be stripped in the sentence
punctuation = '!~`@#$%^&*()_-+={}[]|\\:;"\'?/<>,.'

# takes in a sentence and outputs a list of words of that sentence, all in lowercase
def makelist(sentence):
    return [word.rstrip(punctuation).lstrip(punctuation).lower()
                for word in sentence.split()]

