
inputstring = ('6\nuuuhiullllMMMMMMMMMNNddd\nabcdefghijk\nWWWWWWWWWWWWWWW\nvvVVvvVV\nbbbbsampleoutputooooooooooPPP\nbbleeu\n')
'''
Output:
6
3uhiu4l9M2N3d
abcdefghijk
15W
2v2V2v2V
4bsampleoutput10o3P
2bl2eu
'''
def Runlength(inputstring):
    outputstring = []
    inputstring = inputstring.split('\n')
    wordlist = []
    for w in inputstring:
        if len(w)==0:
            continue
        s = list(w)

        word=[]
        for i in s:
            if len(word)==0:
                word.append(i)
            elif i ==word[-1]:
                word.append(i)
            else:
                if len(word)!=1:
                    wordlist.append(str(len(word)))

                wordlist.append(str(word[0]))
                word = []
                word.append(i)

        if len(word) != 1:
            wordlist.append(str(len(word)))
        wordlist.append(str(word[0]))
        wordlist.append('\n')

    s = ''
    return s.join(wordlist)

#print(Runlength(inputstring))

input = '''
5,10,1
1,1,1
4,2,1
3,10,1
3,25,2
3,5,99
-1,5,4
10,10,1
5,10,0
'''
print(input)
'''
Example output

1 ... 4 5 6 ... 10
1
ERR
1 2 3 4 ... 10
1 2 3 4 5 ... 25
1 2 3 4 5
ERR
1 ... 9 10
1 ... 5 ... 10
'''