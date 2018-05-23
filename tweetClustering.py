#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import copy
import numpy as np
import operator
import random
import collections
from operator import itemgetter
import itertools
import matplotlib.pyplot as plt 
import networkx as nx
import bisect
import os
import csv

"""
Created on Tue May 22 10:25:39 2018

@author: charlesdickens
"""

"""
todo
"""
def tweetClustering(topic):
    cpl = 1
    TranList, TranCumul = tweetGraphGen(topic)
    if cpl:
        TranList, TranCumul = couple1(TranList, TranCumul)
    
    numnodes = len(TranList)
    
    Adj = [[1 if i != j else 0 for i in range(numnodes)] for j in range(numnodes)]
    
    BackwardPathTweet(Adj, TranList, TranCumul)
    print 'finished algorithm'
    
    
def tweetGraphGen(topic):
    lines = []
    with open("./DataFiles/" + topic + ".csv", "r") as f:
        i = 0
        csvreader = csv.reader(f)
        for row in csvreader:
            if (i == 0):
                i = 1
            else:
                lines.append(row)

    weightlist = []
    indexlist = []
    transProbList = []
    
    for tweeta in lines:
        tweetaweights = []
        tweetaindex = []
        b = 0
        for tweetb in lines:
            if (tweeta != tweetb):
                weight = float(tweeta[4]) - float(tweetb[4])
                weight = 2 - abs(weight)
                weight = weight/2 * weight/2
                tweetaweights.append(weight)
                tweetaindex.append(b)
            b = b + 1
        weightlist.append(tweetaweights)
        indexlist.append(tweetaindex)
    
    
    for w in weightlist:
        totalWeight = sum(w)
        transProbList.append([wt / totalWeight for wt in w])
        
    transProbCumulList = []
    transProbCumulList = [list(list_incr(transProbList[v])) for v in range(len(weightlist))]
    
    
        
    return indexlist, transProbCumulList
    

    
    
#return second largest value in list
def max2(x):
    if len(x) < 2:
        return 0.
    y = list(copy.copy(x))
    y.remove(max(y))
    return max(y)
    
#calculate transition values with new coupling
def couple1(TranList, TranCumul):
    #attempt to fix rounding errors
#    TranCumul = [[round(i, 15) for i in j] for j in TranCumul]
    
    n = len(TranList)
    TranProb = [[i[0]]+list(np.diff(i)) for i in TranCumul]
    
    TranProb = [[round(i, 15) for i in j] for j in TranProb]    
    
    #D = sum_{x} max2_{s} p(s->x)   
    mx2 = [max2([TranProb[i][TranList[i].index(j)] for i in range(n) if j in TranList[i]]) for j in range(n)]
    D = sum(mx2) #normalizing factor

    ref = [i/D for i in mx2] #division for each state
    l = [[] for i in TranList]
    q = [[] for i in TranProb]
    r = [[] for i in TranList]
    #assign probabilities to allocated space
    for i in range(n):
        for j in range(n):
            if j in TranList[i]: #neighbors
                k = TranList[i].index(j)
                if TranProb[i][k] > ref[j]: #more probability than allocated space
                    q[i].append(ref[j]) #assign probability
                    l[i].append(j) #state associated with probability
                    r[i].append(TranProb[i][k]-ref[j]) #keep track of remaining probability
                else: #more allocated space than probability
                    q[i].append(TranProb[i][k]) #assign probability
                    l[i].append(j) #state associated with probability
                    q[i].append(ref[j]-TranProb[i][k]) #empty space not assigned
                    l[i].append(-1) #mark as unassigned space
                    r[i].append(0) #no left over
            else: #not neighbors
                q[i].append(ref[j])
                l[i].append(-1) #mark as unassigned
                r[i].append(0)
    
    #fill in remaining probabilities    
    #iterate backwards when filling in probabilities to avoid index problems
    for i in range(n): 
        for j in range(len(l[i])-1, -1, -1): #look for empty spaces
            if l[i][j] == -1:
                for k in range(len(r)-1, -1, -1): #remaining probabilities
                    if r[i][k] > 0:
                        if round(r[i][k], 15) <= round(q[i][j], 15): #more space than probability
                            q[i].insert(j+1, r[i][k])
                            q[i][j] -= r[i][k]
                            l[i].insert(j+1, k)
                            l[i][j] = -1
                            r[i][k] = 0 #no remaining probability for that state                            
                        else: #more probability than space
                            r[i][k] -= q[i][j] #still keep track of remaining probability for that state
                            l[i][j] = k #track which state
                            break
                            
    q = [list(np.cumsum(i)) for i in q] #cumulative sum
    
    #remove remaining -1s from rounding errors
    for i in range(n):
        for j in range(len(l[i])-1, -1, -1):
            if l[i][j] == -1:
                del l[i][j]
                del q[i][j]
                
    #merge parts of list transitioning to same node
    for i in range(n):
        temp = l[i][-1]
        for j in range(len(l[i])-2, -1, -1):
            if l[i][j] == temp:
                del l[i][j]
                del q[i][j]
            else:
                temp = l[i][j]
    
    return l, [[round(i, 15) for i in j] for j in q]

#functions used by algorithm
# Given [a, b, c], returns [a, a+b, a+b+c]
def list_incr(iterable, func=operator.add):
    it = iter(iterable)
    total = next(it)
    yield total
    for element in it:
           total = func(total, element)
           yield total
           
#Given node and uniform random variable, return random neighbor based on weight
def OneStepTransit(TranCumul, TranList,state,ran):
    i=bisect.bisect_left(TranCumul[state],ran)
    return TranList[state][i]

#Given number of nodes, adjacency matrix, and clustering, return edit cost
def cluster_cost(num_nodes, Adj,cluster):
    induced_graph=np.zeros((num_nodes,num_nodes))
    for w in cluster:
        if len(w)>1:
            for e in itertools.combinations(w, 2):
                induced_graph[e[0],e[1]]=1
                induced_graph[e[1],e[0]]=1
    return 0.5*(np.sum(np.not_equal(Adj,induced_graph)))

#Perform CCPivot Algorithm on the graph
def CCPivot(num_nodes, TranList, Adj):
    cluster=[]
    container_users=range(num_nodes)
    
    while len(container_users)!=0:
        k=random.choice(container_users)
        container_users.remove(k)
        cluster.append([k])
        
        for j in sorted(container_users,reverse=True):
            
            if j in TranList[k]:
                cluster[-1].append(j)
                container_users.remove(j)
                
    induced_graph=np.zeros((num_nodes,num_nodes))
    for w in cluster:
        if len(w)>1:
            for e in itertools.combinations(w, 2):
                induced_graph[e[0],e[1]]=1
                induced_graph[e[1],e[0]]=1
    return 0.5*(np.sum(np.not_equal(Adj,induced_graph))),cluster

   # perform CFTP and record clusters along the critical time (refer to paper for critical times)
def BackwardPathTweet(Adj, TranList, TranCumul):
    u=[]
    flag=0 #algorithm is done
    interval=0 #time
    cluster_size_range = [] #cluster sizes at critical times
    cluster_size_median = [] #median cluster size at critical times
    num_clusters = [] #number of clusters at critical times
    coelsce_tracker_users=[] #lists of clusterings
    critical_times=[] #times when node clusters coalesce
    critical_times_cost=[] #edit cost at critical times
    optimal_cluster=[] #clustering with lowest edit cost
    lowest_conductance_cluster = [] #clustering with lowest conductance
    optimal_cost=1e300 #arbitrary large initial value
    lowest_conductance = 1e300
    conductance_values = [] #list to store the conductance value at each critical time
    nodeList = []
    
    
    #generate networkx graph to obtain conductance values of clusterings after each critical time
    nx_Graph = nx.Graph()
    
    for i in range(len(Adj)):
        nx_Graph.add_edges_from([(i, j) for j in range(i, len(Adj[i])) if Adj[i][j] == 1])
            
    nodeList = nx_Graph.nodes()

    text = '' #save output to write to file
    num_nodes = len(Adj) 
    nodes = xrange(num_nodes)
    #start_time = time.time()
    while flag==0:
        interval += 1 #increment time
        current_state=copy.deepcopy(nodes) #reset current state
        w=np.random.uniform(0,1,1) #new RV 
        u.insert(0,w[0])
        
#        text += 'time = -'+str(interval)+'\n'

        #move chains interval number of times according to RVs in u
        for k in range(0, interval):
            current_state=copy.deepcopy(map (lambda x: OneStepTransit(TranCumul, TranList, x,u[k]), current_state))

#        text += 'current state = '+str(current_state)+'\n'
        
        #on first iteration
        if interval==1:    
            A=list(enumerate(current_state)) #(chain number, current node location)
            AA=set(current_state) #nodes currently occupied by chains
            critical_times.append(interval) #first time is critical time
            temp0=[]
            #generate list of clusterings 
            for v in AA: 
                temp0.append([indx for (indx,cr) in A if cr==v])
            coelsce_tracker_users.insert(0,temp0)
            
            #update cost and clustering
            current_cost=cluster_cost(num_nodes, Adj, coelsce_tracker_users[0])
            critical_times_cost.append(current_cost)
            if current_cost<optimal_cost:
                optimal_cost=current_cost
                optimal_cluster=copy.deepcopy(coelsce_tracker_users[0])
            
            #calculate and save the average conductance value to the list  
            conductance_values.append(conductanceCalc(nx_Graph, coelsce_tracker_users[0], nodeList))
            
            #update lowest conductance 
            if conductance_values[len(conductance_values) - 1]<lowest_conductance:
                lowest_conductance=conductance_values[len(conductance_values) - 1]
                lowest_conductance_cluster=copy.deepcopy(coelsce_tracker_users[0])
                lowest_conductance_cost = current_cost
            
            #update cluster size range and median and num_clusters lists
            num_clusters.append(len(coelsce_tracker_users[0]))
            cluster_size_range.append(calcSizeRange(coelsce_tracker_users[0]))
            cluster_size_median.append(calcSizeMedian(coelsce_tracker_users[0]))
            
            text += 'time = -'+str(interval)+'\n'
            text += 'current state = '+str(current_state)+'\n'
            text += 'current clusters = '+str(coelsce_tracker_users)+'\n'                    
                
        #on subsequent iterations
        else:
            #some values from previous iteration
            recent_critical_time=critical_times[-1]
            recent_cluster=copy.deepcopy(coelsce_tracker_users[-1])
            recent_cluster_index=range(len(recent_cluster))
            temp=[]

            #find clusters where chains are also clustered by current state
            #chains clustered in recent_cluster must all move to same state in current_state to merge with any other clusters
            for i in recent_cluster_index:
                if len(set([current_state[j] for j in recent_cluster[i]]))==1:
                    temp.append((i, list(set([current_state[j] for j in recent_cluster[i]]))[0]))

            Z=collections.Counter(map(lambda x: itemgetter(1)(x),temp))
            final_values=[a for (a,b) in Z.items() if b>=2] #states to merge (b>=2 because need 2 clusters to merge)

            #check partial coalescence condition and merge if okay
            equal_count_indicator=[]*len(final_values)
            coelsce_tracker_users.append([])
            for r in final_values: 

                clusters_coelesced=filter(lambda x : x[1]==r,temp) #clusters to merge
                clusters_coelesced_index=map( lambda x: itemgetter(0)(x),clusters_coelesced)

                
                G_index= list(itertools.chain(*[recent_cluster[x] for x in clusters_coelesced_index]))
                G_state=copy.deepcopy(G_index)
                current_G_state=copy.deepcopy(G_state)

                #count occurances of each chain in set of states whos chains are partially coalescing
                mycount=[1]*len(current_G_state)
                for k in range(0, interval):

                    current_G_state=copy.deepcopy(map (lambda x: OneStepTransit (TranCumul, TranList, x,u[k]),current_G_state))

                    for j in range(len(current_G_state)):
                        if current_G_state[j] in G_state: 
                            mycount[j]+=1

                #each chain must have same number of occurances in partially coalescing cluster
                equal_count_indicator.append(mycount.count(mycount[0]) == len(mycount))

                #merge new clusters
                temp2=[]
                if equal_count_indicator[-1]==True:
                    for s in clusters_coelesced_index:
                        temp2.append(recent_cluster[s])
                        recent_cluster_index.remove(s)
                    temp2 = list(itertools.chain(*temp2))
                    coelsce_tracker_users[-1].append(temp2)

            #unchanged clusters
            for r in recent_cluster_index:
                coelsce_tracker_users[-1].append(recent_cluster[r])
            del coelsce_tracker_users[0]

            #update if any changes to clustering
            if any(equal_count_indicator):
                critical_times.append(interval) #save critical time

                current_cost=cluster_cost(num_nodes, Adj, coelsce_tracker_users[0]) #calculate new cost
                critical_times_cost.append(current_cost)
                if current_cost<optimal_cost: #update optimal cost
                    optimal_cost=current_cost
                    optimal_cluster=copy.deepcopy(coelsce_tracker_users[0])
                
                text += 'time = -'+str(interval)+'\n'
                text += 'current state = '+str(current_state)+'\n'
                text += 'current clusters = '+str(coelsce_tracker_users)+'\n'
                
                #calculate and save the average conductance value to the list 
                conductance_values.append(conductanceCalc(nx_Graph, coelsce_tracker_users[0], nodeList))
                
                #update lowest conductance 
                if conductance_values[len(conductance_values) - 1]<lowest_conductance:
                    lowest_conductance=conductance_values[len(conductance_values) - 1]
                    lowest_conductance_cluster=copy.deepcopy(coelsce_tracker_users[0])
                    lowest_conductance_cost = current_cost
                
                #update cluster size range and median and num_clusters lists
                num_clusters.append(len(coelsce_tracker_users[0]))
                cluster_size_range.append(calcSizeRange(coelsce_tracker_users[0]))
                cluster_size_median.append(calcSizeMedian(coelsce_tracker_users[0]))
                
        user_coel_index= (len(set(current_state)) ==1) #all chains coalesce

        #terminate algorithm
        if (interval-critical_times[-1]>=100 or (user_coel_index)):      
            flag=1

    

    #save the conductance value found at the optimal cost time
    conductance_at_lowest_cost = conductanceCalc(nx_Graph, optimal_cluster, nodeList)

    #save a bunch of values
    text += 'critical times = '+str(critical_times)+'\n'
    text += 'critical times cost = '+ str(critical_times_cost)+'\n'
    text += 'optimal cost = '+ str(optimal_cost)+', time = ' + str(critical_times[critical_times_cost.index(optimal_cost)]) + '\n' 
    text += 'lowest conductance = ' + str(lowest_conductance) + ', time = ' + str(conductance_values.index(lowest_conductance)) + '\n'
    text += 'conductance at lowest cost = '+str(conductance_at_lowest_cost)+'\n'
    text += 'cost at lowest conductance = '+str(lowest_conductance_cost)+'\n'
    text += 'lowest cost clusters = '+str(optimal_cluster)+'\n'
    text += 'lowest conductance clusters = '+str(lowest_conductance_cluster)+'\n'
    
    #create directory for output files
    if not os.path.exists('outdir'):
        print 'Creating directory outdir'
        os.mkdir('outdir')
        
    nn = 0
    while os.path.isfile('outdir/output'+str(nn)+'.txt'):
        nn += 1
    with open('outdir/output'+str(nn)+'.txt', 'w') as f:
        f.write(text)
        print "Writing output to 'outdir/output"+str(nn)+".txt'"
    
    #plot a bunch of things
    plt.figure()
    plt.subplot(211)
    plt.plot(critical_times, critical_times_cost, 'r')
    plt.plot(critical_times, critical_times_cost, '*r')
    plt.xlabel('critical times'); plt.ylabel('cost'); 
    plt.subplot(212)
    plt.plot(critical_times, conductance_values, 'b')
    plt.plot(critical_times, conductance_values, '*b')
    plt.xlabel('critical times'); plt.ylabel('Mean Conductance');
    plt.savefig('outdir/plot'+str(nn)+'.png')
    plt.close() 
    
    plt.figure()
    plt.subplot(211)
    plt.plot(critical_times, cluster_size_range, 'r')
    plt.plot(critical_times, cluster_size_range, '*r')
    plt.xlabel('critical times'); plt.ylabel('Size Range'); 
    plt.subplot(212)
    plt.plot(critical_times, cluster_size_median, 'b')
    plt.plot(critical_times, cluster_size_median, '*b')
    plt.xlabel('critical times'); plt.ylabel('Size Median');
    plt.savefig('outdir/plotcommunitysizeinfo'+str(nn)+'.png')
    plt.close() 
    
    plt.figure()
    plt.plot(critical_times, num_clusters, 'r')
    plt.xlabel('critical times'); plt.ylabel('Number of Clusters'); 
    plt.savefig('outdir/plotnumclusters'+str(nn)+'.png')
    plt.close()
    
    
##########################################################################################
#calculate the size range of clusterings
#clustering - the list of communities found by the backwardpath algorithm
def calcSizeRange(clustering):
    
    low = len(clustering[0]) #smallest cluster size intialization
    high = low #greatest cluster size initialization
    
    for i in clustering:
        #compare low and high to size of i and update low and high appropriately
        if low > len(i):
            low = len(i)
        
        if high < len(i):
            high = len(i)
    
    return high - low

##########################################################################################
#calculate the size median of clusterings
#clustering - the list of communities found by the backwardpath algorithm
def calcSizeMedian(clustering):
    
    size_list = [] #list of community sizes
    
    for i in clustering:
        size_list.append(len(i))
    
    return np.median(np.array(size_list))
    

##########################################################################################
#calculate the average conductance of the clusterings
#nx_Grapg - the networkx graph
#clustering - the list of communities found by the backwardpath algorithm
def conductanceCalc(nx_Graph, clustering, nodeList):
    
    conductanceVals = []
    
    for i in clustering:
        #calculate the cutsize of the clustering to the rest of the graph 
        cut_size = len(nx.edge_boundary(nx_Graph, i, list(set(nodeList) - set(i))))
        
        #calculate the volume of the community
        VolumeI = 0
        for j in i:
            VolumeI += nx_Graph.degree(j)
         
        #calculate the volume of the rest of the graph
        VolumeNotI = 0
        for k in i:
            VolumeNotI += nx_Graph.degree(k)
        
        conductanceVals.append((float(cut_size) / float(min(VolumeNotI, VolumeI))))

    return (sum(conductanceVals) / len(conductanceVals))

##########################################################################################
#calculate the size range of clusterings
#clustering - the list of communities found by the backwardpath algorithm
def calcSizeRange(clustering):
    
    low = len(clustering[0]) #smallest cluster size intialization
    high = low #greatest cluster size initialization
    
    for i in clustering:
        #compare low and high to size of i and update low and high appropriately
        if low > len(i):
            low = len(i)
        
        if high < len(i):
            high = len(i)
    
    return high - low

##########################################################################################
#calculate the size median of clusterings
#clustering - the list of communities found by the backwardpath algorithm
def calcSizeMedian(clustering):
    
    size_list = [] #list of community sizes
    
    for i in clustering:
        size_list.append(len(i))
    
    return np.median(np.array(size_list))
    

##########################################################################################
#calculate the average conductance of the clusterings
#nx_Grapg - the networkx graph
#clustering - the list of communities found by the backwardpath algorithm
def conductanceCalc(nx_Graph, clustering, nodeList):
    
    conductanceVals = []
    
    for i in clustering:
        #calculate the cutsize of the clustering to the rest of the graph 
        cut_size = len(nx.edge_boundary(nx_Graph, i, list(set(nodeList) - set(i))))
        
        #calculate the volume of the community
        VolumeI = 0
        for j in i:
            VolumeI += nx_Graph.degree(j)
         
        #calculate the volume of the rest of the graph
        VolumeNotI = 0
        for k in i:
            VolumeNotI += nx_Graph.degree(k)
        
        conductanceVals.append((float(cut_size) / float(min(VolumeNotI, VolumeI))))

    return (sum(conductanceVals) / len(conductanceVals))
