from __future__ import print_function

sentence = "The QUIck brown>> fox's?? jumped@! over the LaZy ?!dog/. please; +_)doge"

punctuation = '!~`@#$%^&*()_-+={}[]|\\:;"\'?/<>,.'

def makelist(sentence):
    return [word.rstrip(punctuation).lstrip(punctuation).lower()
                for word in sentence.split(' ')]

