from sentenceparsing import makelist


# FUCK YOU PYTHON2.5 WHY YOU NO UPDATE YOUR SERVER PYTHON VERSION!
def itertoolsproduct(*args, **kwds):
    # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
    # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
    pools = map(tuple, args) * kwds.get('repeat', 1)
    result = [[]]
    for pool in pools:
        result = [x+[y] for x in result for y in pool]
    for prod in result:
        yield tuple(prod)    
    

sentence = "Bear car seal miew?"

dict1 = { 
	"bear": {'NN': 0.8391, 'VB': 0.161921},
	"car": {'NN': 0.99999, 'VB': .000001},
        "seal": {'NN':1}
}

partset1 = ['NN', 'VB', 'MIEW', 'RAWR', 'WRATHKITTY']



def init_normalize(lis):
    l = len(lis)
    return dict(zip(lis, [1.0/l] * l))
    
partdict1 = init_normalize(partset1)



def iterate(sentence, dictionary, partset):
    return itertoolsproduct(*(dictionary.get(word, partset).keys() for word in makelist(sentence)))


#for i in iterate(sentence, dict1, partdict1): print(i)
