import copy
import numpy as np
from numpy.random import rand
import operator
import random
import collections
from operator import itemgetter
import itertools
import time
import cPickle as pickle
import matplotlib.pyplot as plt 
import scipy
from scipy import stats
import networkx as nx
import math
import cmath
import bisect
import matplotlib
from joblib import Parallel, delayed 
import multiprocessing
import sys
from numpy import linalg as LA
import pylab
from pylab import get_current_fig_manager,show,plt,imshow
import os
import community
import igraph
from NewsCrawlerGraph import newsCrawlerGraph
import newsCrawler2
from MySqlNewsCrawler import MySqlConn


#####################################################################
#read lfr generated files and generate adjacency matrix and communities
def lfr_read(path):
    netf = path+'/network.dat'
    comf = path+'/community.dat'
    edgelist = []
    node_clusters = []
    #create list of community membership
    with open(comf, 'rb') as f:
        for r in f:
            n = int(r.split()[0])-1
            c = int(r.split()[1])-1
            while c >= len(node_clusters):
                node_clusters.append([])
            node_clusters[c].append(n)
    #create adjacency matrix
    n = sum([len(i) for i in node_clusters])
    Adj = np.zeros((n, n))
    with open(netf, 'rb') as f:
        for r in f:
            Adj[int(r.split()[0])-1][int(r.split()[1])-1] = 1
    return Adj, node_clusters

#####################################################################
    #generate news crawler graph
def newsCrawler_gen(topic):
    
    #scrape internet for articles covering topic and add them to sql DB
    newsCrawler2.crawlByTopic(topic)
    
    sqlConn = MySqlConn()
    
    try:
        #USE database for topic
        sqlConn.mySqlDatabase(topic)
        
        #retrieve list of articles
        _,articlesList = sqlConn.retrieveArticles()
        
        #build graph from articles
        NCGraph = newsCrawlerGraph(articlesList)
        
        #get adjacency matrix and nodeIdMap from graph
        Adj = NCGraph.adjMatrix
        nodeIdMap = NCGraph.nodeIdMap
        
    finally:
        #make sure DB connection is closed
        del sqlConn
        
    print Adj
    
    return Adj,nodeIdMap

	
#generates adjacency matrix and communities for stochastic block model
def sbm_gen(sizes, p, q):
    num_nodes = sum(sizes)
    L = [0]+list(list_incr(sizes))
    count = 0
    max_try = 20
    connected = False
    
    #run until connected graph
    while not connected:
        count += 1
        if count > max_try:
            print 'Unsuccessful in creating connected graph'
            return
        
        #create graph by filling upperhalf adjacency matrix
        Adjtemp=np.zeros((num_nodes,num_nodes))
        Adj=np.zeros((num_nodes,num_nodes))
        for i in range(0,len(L)-1): #generate adjacency matrix
            Adjtemp[L[i]:L[i+1],L[i+1]:num_nodes]=copy.deepcopy(scipy.stats.bernoulli.rvs(q, size=(L[i+1]-L[i],num_nodes-L[i+1])))
            for j in range(L[i],L[i+1]):
                Adjtemp[j,j+1:L[i+1]]=copy.deepcopy(scipy.stats.bernoulli.rvs(p, size=(1,-j-1+L[i+1])))
        Adjtemp = Adjtemp+np.transpose(Adjtemp)
                
        #check if connected
        g = nx.Graph()
        for i in range(len(Adjtemp)):
            g.add_edges_from([(i, j) for j in range(i, len(Adjtemp[i])) if Adjtemp[i][j] == 1])
        
        if nx.is_connected(g):
            connected = True
    
    #create community list and randomly reassign membership 
    node_clusters = []
    test = range(num_nodes)
    random.shuffle(test)
    for i in range(0, len(L)-1):
        tem=map(lambda x: test[x], range(L[i], L[i+1]))
        node_clusters.append(tem)
    for u in range(num_nodes):
        for v in range(num_nodes):
            Adj[test[u]][test[v]] = Adjtemp[u][v]

    return Adj, node_clusters

#generates forest fire graph for algorithm
def ffm_gen(num_nodes, fw_prob, bw_factor, ambs):
    g = igraph.GraphBase.Forest_Fire(num_nodes, fw_prob, bw_factor, ambs, False)
        
    Adj = g.get_adjacency()
    
    return Adj
    
    

#calculate transition probabilities and labels
def transval(Adj, node_clusters):

    # Count edge weights
    H = nx.Graph()
    H.add_nodes_from(range(len(Adj)))
    for i in range(len(Adj)):
        H.add_edges_from([(i, j) for j in range(i, len(Adj[i])) if Adj[i][j] == 1])
    
    #computing edge weights based on neighborhood structure
    for e in H.edges():
        H[e[0]][e[1]]['weight']= 1+pow(len(set(H.neighbors(e[0])).intersection(H.neighbors(e[1]))),5)#important factor
    
    TranList=[]
    TranProb=[]
    #for each node, we compute the normalized weight. For example if node 1 has three neighbors [2,3,4], then:
    for v in xrange(H.number_of_nodes()):
        qq=sum([H[v][i]['weight'] for i in list(H.neighbors_iter(v))])
        TranList.append([z for z in H.neighbors_iter(v)])
        TranProb.append([H[v][z]['weight']/float(qq) for z in H.neighbors_iter(v)])
    
    TranCumul = [list(list_incr(TranProb[v])) for v in range(H.number_of_nodes())]
        
    return TranList, TranCumul

#calculate transition probabilities and labels
def transvalffm(Adj):
    # Count edge weights
    H = nx.Graph()
    H.add_nodes_from(range(len(Adj)))
    for i in range(len(Adj)):
        H.add_edges_from([(i, j) for j in range(i, len(Adj[i])) if Adj[i][j] == 1])
    
    #computing edge weights based on neighborhood structure
    for e in H.edges():
        H[e[0]][e[1]]['weight']= 1+pow(len(set(H.neighbors(e[0])).intersection(H.neighbors(e[1]))),5)#important factor
    
    TranList=[]
    TranProb=[]
    #for each node, we compute the normalized wight. For example if node 1 has three neighbors [2,3,4], then:
    for v in xrange(H.number_of_nodes()):
        qq=sum([H[v][i]['weight'] for i in list(H.neighbors_iter(v))])
        TranList.append([z for z in H.neighbors_iter(v)])
        TranProb.append([H[v][z]['weight']/float(qq) for z in H.neighbors_iter(v)])
    
    TranCumul = [list(list_incr(TranProb[v])) for v in range(H.number_of_nodes())]
    
    return TranList, TranCumul

#calculate transition probabilities and labels
def transvalNews(Adj):
    TranList=[]
    TranProb=[]
    
    #for each node, we compute the normalized wight. For example if node 1 has three neighbors [2,3,4], then:
    for v in xrange(len(Adj)):
        qq=sum(Adj[v]) #sum of the row
        TranList.append([z for z in xrange(len(Adj)) if Adj[v][z] != 0])
        TranProb.append([Adj[v][z]/float(qq) for z in xrange(len(Adj)) if Adj[v][z] != 0])
    
    TranCumul = [list(list_incr(TranProb[v])) for v in range(len(Adj))]
    
    return TranList, TranCumul
    
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

#not used
def existing_edges_inside(Adj, subgraph):
    z=Adj[subgraph]
    z=z[:,subgraph]
    return 0.5*sum(sum(z))
	
#not used
def existing_edges_across(Adj,subgraph1,subgraph2):
    z=Adj[subgraph1]
    z=z[:,subgraph2]
    return sum(sum(z))

#not used
def get_image(num_nodes, Adj, cluster):
    cluster=cluster
    test= [item for sublist in cluster for item in sublist]
    Ad=np.zeros((num_nodes,num_nodes))
    for u in xrange(len(test)):
        for v in xrange(len(test)):
            Ad[u][v]=Adj[test[u]][test[v]]

    plt.clf()
    #plt.imshow(Ad, cmap='flag',  interpolation='nearest')
    plt.spy(Ad,cmap='Accent') #Accent
    plt.axis('off')
    path='./AnimFigs'
    filename='bit%d.jpeg' % (image_counter)
    filename = os.path.join(path, filename)
        
    plt.savefig(filename,format='jpeg')
    plt.show()


# draw a circular layout for a given clustering
def draw_graph(node_clusters, nodes, Adj, image_counter, other_cluster=None, CCPivot_cluster=None):
    path='./AnimFigs'
    alg_cluster=other_cluster
    CCPivot_cluster=CCPivot_cluster

#    arraymap=np.array(node_clusters)
#    community=map(lambda x:np.where(arraymap == x)[0][0], list(nodes))
       
    comm_idx = [0]*len(nodes)
    for i in range(len(node_clusters)):
        for j in node_clusters[i]:
            comm_idx[j] = i
    
    B = nx.Graph()
    edge_list=[]
    for r in itertools.izip(np.nonzero(Adj)[0],np.nonzero(Adj)[1]):
        B.add_edge(nodes[r[0]], nodes[r[1]])
    cmapp=matplotlib.colors.cnames.keys()
    mycolors=np.random.choice(cmapp,len(node_clusters),replace=False)
    #mycolors=['red','blue','green','orange','brown','yellow','cyan']


    OrigPos={}
    R=np.average(map(len,node_clusters))   
    centers=points(len(node_clusters),[0,0],.8*R)
    for w in range(len(node_clusters)):
        newcenter=centers[w]
        newpoints=points(len(node_clusters[w]),newcenter,1.5*R/float(len(node_clusters)))
        newpoints=map(tuple,newpoints)
        for v in range(len(node_clusters[w])):
            OrigPos.update( {node_clusters[w][v]:newpoints[v]} )
    nx.draw_networkx_edges(B,pos=OrigPos,width=.3,arrows=False, style='solid',alpha=1,edge_color='k')
    for w in range(len(node_clusters)):
        nx.draw_networkx_nodes(B,pos=OrigPos,node_size=120,nodelist=node_clusters[w], node_color=map(lambda x: mycolors[w],node_clusters[w]),font_color="k",font_size=4,width=1,alpha=1)
    #nx.draw_networkx_labels(B,pos=OrigPos, font_size=10)
    plt.figure(1)
    plt.axis('off')
    #plt.title('Original Network')

    if alg_cluster!=None:
        pos={}
        R=np.average(map(len,alg_cluster))
        centers=points(len(alg_cluster),[0,0],.8*R)
        for w in range(len(alg_cluster)):
            newcenter=centers[w]
            newpoints=points(len(alg_cluster[w]),newcenter,1.5*R/float(len(alg_cluster)))
            newpoints=map(tuple,newpoints)
            for v in range(len(alg_cluster[w])):
                pos.update( {alg_cluster[w][v]:newpoints[v]} )
        
        plt.clf()
        plt.figure(1)
        #plt.title('Our Algorithm Output')
        plt.axis('off')
        #nx.draw_networkx_edges(B,pos=pos,width=.07,arrows=False, style='solid',alpha=1,edge_color='k')
        for w in range(len(alg_cluster)):
            nx.draw_networkx_nodes(B,pos=pos,node_size=20,nodelist=alg_cluster[w], node_color=map(lambda x: mycolors[ comm_idx[x]],alg_cluster[w]),font_color="k",font_size=5,linewidths=None,alpha=1)
        #nx.draw_networkx_labels(B,pos=pos, font_size=10)
        filename='fig%d.jpeg' % (image_counter)
        print filename
        filename = os.path.join(path, filename)
        
        plt.savefig(filename,format='jpeg')

#Used in draw_graph()
def points(k,cen,r):
    p=[]
    for k in np.arange(-math.pi, math.pi, 2*math.pi/float(k)):
        p.append([cmath.rect(r,k).real,cmath.rect(r,k).imag])
    return map(lambda x: [x[0]+cen[0],x[1]+cen[1]],p)

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


def ComapreCost():
    return BackwardPath()[0] , CCPivot()[0], girwan_cost

# perform CFTP and record clusters along the critical time (refer to paper for critical times)
def BackwardPath(Adj, node_clusters, TranList, TranCumul):
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
    optimal_cost=1e300 #arbitrary large initial value
    lowest_conductance = 1e300
    conductance_values = [] #list to store the conductance value at each critical time
    nodeList = []
    lowest_conductance_cluster = [] #clustering with lowest conductance

    image_counter=0 #number circular plots
    
    #generate networkx graph to obtain conductance values of clusterings after each critical time
    nx_Graph = nx.Graph()
    
    for i in range(len(Adj)):
        nx_Graph.add_edges_from([(i, j) for j in range(i, len(Adj[i])) if Adj[i][j] == 1])
            
    nodeList = nx_Graph.nodes()
    
    #create directory for drawings
    if not os.path.exists('AnimFigs'):
        print 'Creating directory AnimFigs'
        os.mkdir('AnimFigs')

    nmi_v = [] #store normalized mutual information
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
            nmi_v.append(nmi_calc(node_clusters, coelsce_tracker_users[0]))
                
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
                image_counter+=1
                draw_graph(node_clusters, nodes, Adj, image_counter, coelsce_tracker_users[0],None)

                current_cost=cluster_cost(num_nodes, Adj, coelsce_tracker_users[0]) #calculate new cost
                critical_times_cost.append(current_cost)
                if current_cost<optimal_cost: #update cost
                    optimal_cost=current_cost
                    optimal_cluster=copy.deepcopy(coelsce_tracker_users[0])
                
                text += 'time = -'+str(interval)+'\n'
                text += 'current state = '+str(current_state)+'\n'
                text += 'current clusters = '+str(coelsce_tracker_users)+'\n'
                nmi_v.append(nmi_calc(node_clusters, coelsce_tracker_users[0]))
                
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

    nmi = nmi_calc(node_clusters, optimal_cluster)
    
    #save the conductance value found at the optimal cost time
    conductance_at_lowest_cost = conductanceCalc(nx_Graph, optimal_cluster, nodeList)

    #save a bunch of values
    text += 'critical times = '+str(critical_times)+'\n'
    text += 'critical times cost = '+ str(critical_times_cost)+'\n'
    text += 'normalized mutual information = '+str(nmi_v)+'\n'
    text += 'optimal cost = '+ str(optimal_cost)+', time = ' + str(critical_times[critical_times_cost.index(optimal_cost)]) + '\n'
    text += 'lowest conductance = ' + str(lowest_conductance) + ', time = ' + str(conductance_values.index(lowest_conductance)) + '\n'
    text += 'conductance at lowest cost = '+str(conductance_at_lowest_cost)+'\n'
    text += 'cost at lowest conductance = '+str(lowest_conductance_cost)+'\n'
    text += 'lowest cost clusters = '+str(optimal_cluster)+'\n'
    text += 'correct clusters = '+str(node_clusters)+'\n'    
    text += 'recovered clusters = '+str(optimal_cluster)+'\n'
    text += 'lowest conductance clusters = '+str(lowest_conductance_cluster)+'\n'
    text += 'nmi = '+str(nmi)+'\n'
    
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
    plt.plot(critical_times, nmi_v, 'b')
    plt.plot(critical_times, nmi_v, '*b')
    plt.xlabel('critical times'); plt.ylabel('nmi (b)');
    plt.savefig('outdir/plot'+str(nn)+'.png')
    plt.close
    
    plt.figure()
    plt.subplot(211)
    plt.plot(critical_times, conductance_values, 'b')
    plt.plot(critical_times, conductance_values, '*b')
    plt.xlabel('critical times'); plt.ylabel('Mean Conductance');
    plt.subplot(212)
    plt.plot(critical_times, nmi_v, 'b')
    plt.plot(critical_times, nmi_v, '*b')
    plt.xlabel('critical times'); plt.ylabel('nmi (b)');
    plt.savefig('outdir/plotconductance'+str(nn)+'.png')
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
    
    #to check accuracy
    return nmi

# perform CFTP and record clusters along the critical time (refer to paper for critical times)
def BackwardPathffm(Adj, TranList, TranCumul):
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
    
    
    # perform CFTP and record clusters along the critical time (refer to paper for critical times)
def BackwardPathNewsCrawler(Adj, TranList, TranCumul, nodeIdMap):
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
    text += 'Node to Article Mapping =' + str(nodeIdMap) + '\n'

    
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
#calculate normalized mutual information, given real and found communities
#real- list of lists of nodes in actual communities
#found- list of lists of nodes in communities found by algorithm
def nmi_calc(real, found):
    #populate confusion matrix
    #conf[i][j] = number of nodes in real community i that appear in found community j
    conf = np.zeros((len(real), len(found)))
    for i in range(len(real)):
        for j in range(len(found)):
            conf[i][j] = len(set(real[i]).intersection(set(found[j])))
    N_row = [len(i) for i in real]
    N_col = [len(i) for i in found]
    N = sum(N_row)
    num = 0
    for i in range(len(real)):
        for j in range(len(found)):
            if conf[i][j] != 0:
                num += conf[i][j]*np.log(float(conf[i][j]*N)/(N_row[i]*N_col[j]))
    den1 = sum([N_row[i]*np.log(float(N_row[i])/N) for i in range(len(real))])
    den2 = sum([N_col[j]*np.log(float(N_col[j])/N) for j in range(len(found))])
    return -2*num/(den1+den2)
##########################################################################################
##########################################################################################

#These two functions run the algorithm on an sbm and lfr graph, respectively

#sizes is a list of the sizes of communities (length of list is number of communities)
#p is the probability of an edge between nodes in the same community
#q is the probability of an edge between nodes in different communities
def sbm(sizes, p, q, cpl=1):
    t0 = time.time()
    Adj, node_clusters = sbm_gen(sizes, p, q)
    t1 = time.time()
    print 'created graph in '+str(t1-t0)+' sec'
    TranList, TranCumul = transval(Adj, node_clusters)
    t2 = time.time()
    print 'calculated some values in '+str(t2-t1)+' sec'
    if cpl:
        TranList, TranCumul = couple1(TranList, TranCumul)
    t3 = time.time()
    print 'calculated some more values '+str(t3-t2)+' sec'
    nmi = BackwardPath(Adj, node_clusters, TranList, TranCumul)
    t4 = time.time()
    print 'finished algorithm in '+str(t4-t3)+' sec'
    print 'total run time '+str(t4-t0)+' sec'
#    t = [t0, t1, t2, t3, t4]
    return nmi

#runs the algorithm on the forest_fire model graph generated by the igraph package
def ffm(num_nodes, fw_prob, bw_factor, ambs):
    t0 = time.time()
    cpl = 1
    Adj = ffm_gen(num_nodes, fw_prob, bw_factor, ambs)
    t1 = time.time()
    print 'created graph in '+str(t1-t0)+' sec'
    TranList, TranCumul = transvalffm(Adj)
    t2 = time.time()
    print 'calculated some values in '+str(t2-t1)+' sec'
    if cpl:
        TranList, TranCumul = couple1(TranList, TranCumul)
    t3 = time.time()
    print 'calculated some more values '+str(t3-t2)+' sec'
    BackwardPathffm(Adj, TranList, TranCumul)
    t4 = time.time()
    print 'finished algorithm in '+str(t4-t3)+' sec'
    print 'total run time '+str(t4-t0)+' sec'
    

def newsCrawl(topic):
    t0 = time.time()
    cpl = 1
    Adj,nodeIdMap = newsCrawler_gen(topic)
    t1 = time.time()
    print 'Scraped new articles and created graph in '+str(t1-t0)+' sec'
    TranList, TranCumul = transvalNews(Adj)
    t2 = time.time()
    print 'calculated some values in '+str(t2-t1)+' sec'
    if cpl:
        TranList, TranCumul = couple1(TranList, TranCumul)
    t3 = time.time()
    print 'calculated some more values '+str(t3-t2)+' sec'
    #update so Adj is unweighted, for BackwardPath alg
    Adj = [[1 if Adj[i][j] > 0 else 0 for j in xrange(len(Adj))] for i in xrange(len(Adj))]
    BackwardPathNewsCrawler(Adj, TranList, TranCumul, nodeIdMap)
    t4 = time.time()
    print 'finished algorithm in '+str(t4-t3)+' sec'
    print 'total run time '+str(t4-t0)+' sec'
    

def timesbm(sizes, p, q):
    t0 = time.time()
    Adj, node_clusters = sbm_gen(sizes, p, q)
    t1 = time.time()
    print 'created graph in '+str(t1-t0)+' sec'
    TranList, TranCumul = transval(Adj, node_clusters)
    t2 = time.time()
    print 'calculated some values in '+str(t2-t1)+' sec'
    newTranList, newTranCumul = couple1(TranList, TranCumul)
    t3 = time.time()
    print 'calculated some more values '+str(t3-t2)+' sec'
    nmi = BackwardPath(Adj, node_clusters, TranList, TranCumul)
    t4 = time.time()
    print 'finished uncoupled algorithm in '+str(t4-t0)+' sec'
    nmic = BackwardPath(Adj, node_clusters, newTranList, newTranCumul)
    t5 = time.time()
    print 'finished coupled algorithm in '+str(t5-t4)+' sec'
    print 'total run time '+str(t5-t0)+' sec'
    t = [t3-t2, t4-t3, t5-t4]
    return nmi, nmic, t

#path is the folder that contains the files generated from the lfr code
def lfr(path):
    cpl = 1
    t0 = time.time()
    Adj, node_clusters = lfr_read(path)
    t1 = time.time()
    print 'created graph in '+str(t1-t0)+' sec'
    TranList, TranCumul = transval(Adj, node_clusters)
    t2 = time.time()
    print 'calculated some values in '+str(t2-t1)+' sec'
    if cpl:
        TranList, TranCumul = couple1(TranList, TranCumul)
    t3 = time.time()
    print 'calculated some more values '+str(t3-t2)+' sec'
    nmi = BackwardPath(Adj, node_clusters, TranList, TranCumul)
    t4 = time.time()
    print 'finished algorithm in '+str(t4-t3)+' sec'
    print 'total run time '+str(t4-t0)+' sec'
#    t = [t0, t1, t2, t3, t4]
    return nmi

##########################################################################################
def mu_sbm(p, q, c):
    return q*(c-1)/(p+q*(c-1))
##########################################################################################
##########################################################################################
#run algorithm on sbm graph for a variety of parameters and write nmi to file
#n = 2000
#pq_list1 = [(.6, .07), (.75, .08), (.9, .1), (.6, .2), (.75, .25), (.9, .3), (.6, .4), (.75, .5), (.9, .6)]
#pq_list2 = [(.6, .017), (.75, .021), (.9, .025), (.6, .05), (.75, .062), (.9, .075), (.6, .1), (.75, .13), (.9, .15)]
#for pq in pq_list2:
#    for i in range(5):
#        t0 = time.time()
#        nmi = sbm([n/2]*2, pq[0], pq[1])
#        with open('sbm_data.txt', 'a') as f:
#            f.write(str(pq)+' '+str(nmi)+' '+str(time.time()-t0)+'\n')
#            
#run algorithm on variety of lfr graphs and write nmi to file
#for pq in pq_list1:
#    for i in range(5):
#        t0 = time.time()
#        nmi = sbm([n/5]*5, pq[0], pq[1])
#        with open('sbm_data.txt', 'a') as f:
#            f.write(str(pq)+' '+str(nmi)+' '+str(time.time()-t0)+'\n')

#
#lfr('benchmark_2_1/graph0/')
            
###########
#p = .6
#q = .4
#sizes = [400]*5
#for i in range(5):
#    a = sbm(sizes, p, q)
#    print 'nmi = '+str(a)

##############################
#run algorithm to compare run times
#
#num = 10
##sizes_ = [[100, 100]]
#sizes_ = [[2000, 2000]]
##pq_ = [(0.8, 0.2)]
#pq_ = [(0.2, 0.05)]
#for sizes in sizes_:
#    for pq in pq_:
#        for i in range(num):
#            nmi, nmic, t = timesbm(sizes, pq[0], pq[1])
#            with open('/home/kevin/research/slow_mixing_code/times4.txt', 'a') as f:
#                f.write(str(nmi)+'\t'+str(nmic)+'\t'+str(round(t[0], 2))+'\t'+str(round(t[1], 2))+'\t'+str(round(t[2], 2))+'\n')

###############################
#nmi = sbm([5]*3, 0.8, 0.2)
#nmi = lfr('benchmark_2_1/graph'+str(i))
#print nmi
###############################
# write a for loop to run the algorithm on each of the graphs and write the nmi to a file
#generate 3 graphs for each set of parameters (27 total graphs)
#number of nodes 200, 1000, 2000
#avg deg 20
#max deg 50
#deg distr exp 1
#comm size exp 2
#mixing parameter 0.2, 0.4, 0.6
#min comm size 10
#max comm size 200