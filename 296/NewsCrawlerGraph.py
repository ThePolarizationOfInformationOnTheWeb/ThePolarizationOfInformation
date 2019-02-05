#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 14:05:33 2017

@author: charlesdickens

file:        newsCrawlerGraph.py

description: This script contains the newsCrawlerGraph class which contects  
             articles covering a news topic as nodes to other articles with 
             calculated edge weights based on parameters such as longest 
             common subsequence.
"""
from __future__ import division
import LCS
import nltk

class newsCrawlerGraph:
    
    adjMatrix = [] ## adjMatrix[row][column] = directed edge weight from row 
                   ## to column
    nodeIdMap = {} ## nodeIdMap[(domain, headline)] = id num 
    contents = []   ## contents[id num] = article content with id num
    
    """
    function:    __init__

    parameters:  articles : a list of 3-tuples (domain, headline, content)
    description: from articles list the adjacency matrix describing the graph
                 is built by calling the addArticle method for each article 
                 in the list.
    """
    def __init__(self, articles = []):
        
        ## iterate through all the articles in the list and add them to the graph
        for domain, headline, content in articles:
            self.addArticle(domain, headline, content)
    """
    function:    addArticle

    parameters:  domain   : article's domain
                 headline : article's headline
                 content  : article's content
    description: adds article to graph with edge to other articles based on
                 calcEdgeWeights method
    """
    def addArticle(self, domain, headline, content):
        #calculate and retrieve edge weight list for article
        edgeWeights = self.__calcEdgeWeights(content)
        
        #add article to nodeIdMap to keep track of its index in the adjMatrix
        idNum = len(self.adjMatrix)
        self.nodeIdMap[(domain, headline)] = idNum
        
        #add content to contents list for future reference
        self.contents.append(content)
        
        #add row for new node with edges
        self.adjMatrix.append(edgeWeights)
        
        #add self loop weight 0
        #self.adjMatrix[idNum].append(0)
        
        #make column in matrix so connections are symmetric
        for i in range(len(edgeWeights) - 1):
            self.adjMatrix[i].append(edgeWeights[i])
        
    
    """
    function:    __calcEdgeWeights

    parameters:  content  : article's content
    description: calculates the edge wieghts of the article if it were added as
                 a new node to the existing adjMatrix, returns edge weights as
                 a list where the entry at index i of the list corresponds to 
                 the edge weight connecting the article to the article with 
                 id number i.
    """
    def __calcEdgeWeights(self, content):
        
        edgeWeights = [] #holds the edge weight values where entry at index i is
                         #the edge weight from the new article to the article with
                         #id number i
        
        c2 = content.lower()
        Arr2len = len(c2)
        c2 = nltk.word_tokenize(c2)
        tagged2 = nltk.pos_tag(c2)
        c1 = [w for w,t in tagged2 if t != "DT" and t != "IN" and t != "WP" 
              and t != "WRB" and t!= "WP$" and t != "WDT" and t != "EX"
              and t != "TO" and t != "RP"]
        c2 = c2[0:500]
        
        for i in range(len(self.contents)):
            c1 = self.contents[i].lower()
            Arr1len = len(c1)
            c1 = nltk.word_tokenize(c1)
            tagged1 = nltk.pos_tag(c1)
            c1 = [w for w,t in tagged1 if t != "DT" and t != "IN" and t != "WP" 
                  and t != "WRB" and t!= "WP$" and t != "WDT" and t != "EX"
                  and t != "TO" and t != "RP"]
            c1 = c1[0:500]
            
            weight = LCS.LCS(c1, c2)
            
            weight = weight / ((Arr1len + Arr2len) / 2)
            
            #weight = weight * weight
            
            edgeWeights.append(weight)
            
        edgeWeights.append(0)
        return edgeWeights
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        