#!/usr/bin/python -u
#
# http://tools.qhex.org/

#import sys
import dictionaryTEST as dictionary

class caesarshift():

    MAX_WORD_LEN = 20
        
    def rot(self,s, n):
        result = ''
        for c in s:
            x = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.find(c.upper())
            if x != -1:
                new_c = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[(x + n) % 26]
                if c == c.lower():
                    new_c = new_c.lower()
                result += new_c
            else:
                result += c
        return result
    
    def highlight(self,s):
        '''Returns a string of '^' characters highlighting any words in s.'''
        result = [' '] * len(s)
        for i in range(len(s)):
            for j in range(i, min(len(s) + 1, i + self.MAX_WORD_LEN)):
                score = dictionary.score(s[i:j].lower())
                if score > 0 and j-i+score > 7:  # ignore short rare words
                    for k in range(i, j):
                        result[k] = '^'
        return ''.join(result)
    
    def run(self,strin):
        a = ''
        for n in range(26):
            s = self.rot(strin, n)
            a =a+('+'+str(n)).rjust(3)+' '+ ('-'+str((26-n)%26)).rjust(3)+ ' '+s +'\n        '+self.highlight(s)+'\n'
        return a