import copy
import numpy as np
import operator
import random
import collections
from operator import itemgetter
import itertools
import time
import networkx as nx
import math
import cmath
import bisect
import matplotlib
from pylab import plt
import os


#calculate transition probabilities and labels
def transval(Adj):

    # Count edge weights
    network = nx.Graph()
    network.add_nodes_from(range(len(Adj)))
    for i in range(len(Adj)):
        network.add_edges_from([(i, j) for j in range(i, len(Adj[i])) if Adj[i][j] == 1])
    
    #computing edge weights based on neighborhood structure
    for e in network.edges():
        network[e[0]][e[1]]['weight']= 1+pow(len(set(network.neighbors(e[0])).intersection(network.neighbors(e[1]))),5)#important factor
    
    TranList=[]
    TranProb=[]
    #for each node, we compute the normalized weight. For example if node 1 has three neighbors [2,3,4], then:
    for v in range(network.number_of_nodes()):
        qq=sum([network[v][i]['weight'] for i in list(network.neighbors(v))])
        TranList.append([z for z in network.neighbors(v)])
        TranProb.append([network[v][z]['weight']/float(qq) for z in network.neighbors(v)])
    
    TranCumul = [list(list_incr(TranProb[v])) for v in range(network.number_of_nodes())]
    
        
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
    n = len(TranList)
    #from the Cumulative distribution calculate the probability mass function
    TranProb = [[i[0]]+list(np.diff(i)) for i in TranCumul]
    #cut off at 15 decimal places of precision
    TranProb = [[round(i, 15) for i in j] for j in TranProb]    
    
    #D = sum_{x} max2_{s} p(s->x) 
    #mx2 is the list of the 2nd largest inward edge transition probabilities 
    #for all the nodes, i.e. if Ej is the set of edges with terminating vertex 
    #j, then Tj is the list of transition probabilities corresponding to the 
    #edges in Ej, then mx2[j] is the 2nd largest element of Tj.
    mx2 = [max2([TranProb[i][TranList[i].index(j)] for i in range(n) if j in TranList[i]]) for j in range(n)]
    #D is the sum of all the sum of all the 2nd largest inward edge transition 
    #probabilities, we call D our normalizing factor for mx2.
    D = sum(mx2)

    #ref is the list of the 2nd largest inward edge transition probabilities 
    #for all the nodes divided by the normalizing factor setting each value of 
    #ref to be between 0 and 1, the sum of ref should be 1.
    ref = [i/D for i in mx2] #division for each state
    #l,q, and r are lists of empty lists, 1 list for each entry in TranList, 
    #i.e. 1 list for each node.
    l = [[] for _ in TranList] #the states associated with transition
    q = [[] for _ in TranProb] #the transition probabilities, if l[i][j] is -1 
                               #then this holds the remaing probability mass 
                               #from ref[j] 
    r = [[] for _ in TranList] #the remaining probability mass from original 
                               #transition probabilities
    #assign probabilities to allocated space
    for i in range(n): #recall n is the number of nodes in our graph
        for j in range(n):
            if j in TranList[i]: #there exists a directed edge, e, from i to j 
                k = TranList[i].index(j) #k is the index to find the 
                                         #corresponding transition probability
                                         #for traversing e when you are at 
                                         #state i.
                if TranProb[i][k] > ref[j]: #more probability than allocated 
                                            #space. i.e. the transition 
                                            #probability from node i to j is 
                                            #larger than the 2nd largest 
                                            #transition probability with j as
                                            #the terminating node divided by D
                    q[i].append(ref[j]) #assign probability, the value in ref[j]
                    l[i].append(j) #state associated with probability, i.e. node
                    r[i].append(TranProb[i][k]-ref[j]) #keep track of remaining 
                                                       #probability. we find the 
                                                       #difference between the 
                                                       #original transition 
                                                       #probability and ref[j]
                else: #more allocated space than probability. i.e. the transition 
                      #probability from node i to j is less than or equal to the 
                      #2nd largest transition probability with j as the terminating 
                      #node divided by D
                    l[i].append(j) #state associated with probability, i.e. node
                    q[i].append(TranProb[i][k]) #assign probability, the original
                                                #transition probability
                    l[i].append(-1) #mark as unassigned space
                    q[i].append(ref[j]-TranProb[i][k]) #empty space not assigned,
                                                       #difference between ref[j] 
                                                       #and the original 
                                                       #transition probbability,
                    r[i].append(0) #no left over probability mass from the 
                                   #original transition probability
            else: #not neighbors, i.e. original transition probability is 0 
                  #from i to j
                q[i].append(ref[j]) #empty space not assigned, all of ref[j]
                l[i].append(-1) #mark as unassigned
                r[i].append(0)
    
    #fill in remaining probabilities    
    #iterate backwards when filling in probabilities to avoid index problems
    for i in range(n): 
        for j in range(len(l[i])-1, -1, -1): #look for empty spaces, iterate 
                                             #through a list of indices for l[i]
                                             #in reverse order
            if l[i][j] == -1: #there is left over probability mass from ref[j] 
                              #that may be assigned 
                for k in range(len(r)-1, -1, -1): #iterate over all indices of 
                                                  #r in reverse order
                    if r[i][k] > 0: #there is left over mass from the original
                                    #transition probability that has yet to be 
                                    #assigned
                        if round(r[i][k], 15) <= round(q[i][j], 15): 
                            #more space than probability, i.e. there is more 
                            #probability mass left from ref[j] than there is 
                            #left over original transition probability mass that
                            #has not been assigned yet
                            q[i].insert(j+1, r[i][k]) #add transistion probability
                            q[i][j] -= r[i][k] #update left over space from ref[j]
                            l[i].insert(j+1, k) #add corresponging state (node)
                                                #for transition
                            l[i][j] = -1 #there is still some space left to 
                                         #allocate from ref[j]
                            r[i][k] = 0 #no remaining probability mass for that 
                                        #state (node)                          
                        else: #more probability than space
                            r[i][k] -= q[i][j] #still keep track of remaining probability for that state
                            l[i][j] = k #track which state
                            break
                            
    q = [list(np.cumsum(i)) for i in q]#new cdf for transition probabilities
    
    #remove remaining -s from rounding errors
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

# draw a circular layout for a given clustering
def draw_graph(node_clusters, nodes, adj, image_counter, other_cluster=None, ccpivot_cluster=None):
    path='./AnimFigs'
    alg_cluster=other_cluster

    comm_idx = [0]*len(nodes)
    for i in range(len(node_clusters)):
        for j in node_clusters[i]:
            comm_idx[j] = i
    
    B = nx.Graph()
    for r in zip(np.nonzero(adj)[0], np.nonzero(adj)[1]):
        B.add_edge(nodes[r[0]], nodes[r[1]])
    cmapp=matplotlib.colors.cnames.keys()
    mycolors=np.random.choice(cmapp,len(node_clusters),replace=False)

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
    
