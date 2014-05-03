from __future__ import print_function

def f(x): return "" != x
while(True):
	var = filter (f,raw_input("Please enter something: ").split("."))
	print (var)
