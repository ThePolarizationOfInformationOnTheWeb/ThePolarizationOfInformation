#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 07:28:09 2017

@author: charlesdickens
"""

"""
function:    LCS(), Longest Common Subsequence

parameters:  Arr1:    Array 1
             Arr2:    Array 2

description: Given the two string arrays Arr1 and Arr2 LCS will return a list of the
             longest common subsequences. To solve this problem we use
             dynamic programming and memoization.
"""
def LCS(Arr1, Arr2):

    #store lengths of Arr1 and Arr2
    n = len(Arr1)
    m = len(Arr2)

    #build n + 1 x m + 1 memoization table initializing every entry to 0
    MemTbl = [ [0 for x in range(m + 1)] for y in range(n + 1) ]

    #fill in memoization table bottom up, i.e., starting at 1st row and
    #moving from 1st, to 2nd, ..., to (m+1)th column then to 2nd row and so on
    for i in xrange(n + 1):
        for j in xrange(m + 1):
            if i == 0 or j == 0:
                continue
            elif Arr1[i - 1] == Arr2[j - 1]:
                MemTbl[i][j] = (MemTbl[i-1][j-1] + 1)
            else:
                MemTbl[i][j] = max(MemTbl[i-1][j], MemTbl[i][j-1])

    return MemTbl[n][m]
