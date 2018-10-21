import copy
import numpy as np
import operator
import collections
import itertools
import bisect
from operator import itemgetter


def transval(adj):
    TranList = []
    TranProb = []

    for v in range(len(adj)):
        qq = sum(adj[v])  # sum of the row
        TranList.append([z for z in range(len(adj)) if adj[v][z] != 0])
        TranProb.append([adj[v][z] / float(qq) for z in range(len(adj)) if adj[v][z] != 0])

    TranCumul = [list(list_incr(TranProb[v])) for v in range(len(adj))]

    return couple(TranList, TranCumul)


def couple(TranList, TranCumul):
    """
    calculate transition values with new coupling
    :param TranList: The list of nodes and their neighbors
    :param TranCumul: The cumulative distribution corresponding to tranlist
    :return:
    """
    n = len(TranList)
    # from the Cumulative distribution calculate the probability mass function
    TranProb = [[i[0]] + list(np.diff(i)) for i in TranCumul]
    # cut off at 15 decimal places of precision
    TranProb = [[round(i, 15) for i in j] for j in TranProb]

    # D = sum_{x} max2_{s} p(s->x)
    # mx2 is the list of the 2nd largest inward edge transition probabilities
    # for all the nodes, i.e. if Ej is the set of edges with terminating vertex
    # j, then Tj is the list of transition probabilities corresponding to the
    # edges in Ej, then mx2[j] is the 2nd largest element of Tj.
    mx2 = [max2([TranProb[i][TranList[i].index(j)] for i in range(n) if j in TranList[i]]) for j in range(n)]

    # D is the sum of all the sum of all the 2nd largest inward edge transition
    # probabilities, we call D our normalizing factor for mx2.
    D = sum(mx2)

    # ref is the list of the 2nd largest inward edge transition probabilities
    # for all the nodes divided by the normalizing factor setting each value of
    # ref to be between 0 and 1, the sum of ref should be 1.
    ref = [i / D for i in mx2]  # division for each state
    # l,q, and r are lists of empty lists, 1 list for each entry in TranList,
    # i.e. 1 list for each node.
    l = [[] for _ in TranList]  # the states associated with transition
    q = [[] for _ in TranProb]  # the transition probabilities, if l[i][j] is -1
    # then this holds the remaing probability mass
    # from ref[j]
    r = [[] for _ in TranList]  # the remaining probability mass from original
    # transition probabilities
    # assign probabilities to allocated space
    for i in range(n):  # recall n is the number of nodes in our graph
        for j in range(n):
            if j in TranList[i]:  # there exists a directed edge, e, from i to j
                k = TranList[i].index(j)  # k is the index to find the
                # corresponding transition probability
                # for traversing e when you are at
                # state i.
                if TranProb[i][k] > ref[j]:  # more probability than allocated
                    # space. i.e. the transition
                    # probability from node i to j is
                    # larger than the 2nd largest
                    # transition probability with j as
                    # the terminating node divided by D
                    q[i].append(ref[j])  # assign probability, the value in ref[j]
                    l[i].append(j)  # state associated with probability, i.e. node
                    r[i].append(TranProb[i][k] - ref[j])  # keep track of remaining
                    # probability. we find the
                    # difference between the
                    # original transition
                    # probability and ref[j]
                else:  # more allocated space than probability. i.e. the transition
                    # probability from node i to j is less than or equal to the
                    # 2nd largest transition probability with j as the terminating
                    # node divided by D
                    l[i].append(j)  # state associated with probability, i.e. node
                    q[i].append(TranProb[i][k])  # assign probability, the original
                    # transition probability
                    l[i].append(-1)  # mark as unassigned space
                    q[i].append(ref[j] - TranProb[i][k])  # empty space not assigned,
                    # difference between ref[j]
                    # and the original
                    # transition probbability,
                    r[i].append(0)  # no left over probability mass from the
                    # original transition probability
            else:  # not neighbors, i.e. original transition probability is 0
                # from i to j
                q[i].append(ref[j])  # empty space not assigned, all of ref[j]
                l[i].append(-1)  # mark as unassigned
                r[i].append(0)

    # fill in remaining probabilities
    # iterate backwards when filling in probabilities to avoid index problems
    for i in range(n):
        for j in range(len(l[i]) - 1, -1, -1):  # look for empty spaces, iterate
            # through a list of indices for l[i]
            # in reverse order
            if l[i][j] == -1:  # there is left over probability mass from ref[j]
                # that may be assigned
                for k in range(len(r) - 1, -1, -1):  # iterate over all indices of
                    # r in reverse order
                    if r[i][k] > 0:  # there is left-over mass from the original
                        # transition probability that has yet to be
                        # assigned
                        if round(r[i][k], 15) <= round(q[i][j], 15):
                            # more space than probability, i.e. there is more
                            # probability mass left from ref[j] than there is
                            # left over original transition probability mass that
                            # has not been assigned yet
                            q[i].insert(j + 1, r[i][k])  # add transistion probability
                            q[i][j] -= r[i][k]  # update left over space from ref[j]
                            l[i].insert(j + 1, k)  # add corresponging state (node)
                            # for transition
                            l[i][j] = -1  # there is still some space left to
                            # allocate from ref[j]
                            r[i][k] = 0  # no remaining probability mass for that
                            # state (node)
                        else:  # more probability than space
                            r[i][k] -= q[i][j]  # still keep track of remaining probability for that state
                            l[i][j] = k  # track which state
                            break

    q = [list(np.cumsum(i)) for i in q]  # new cdf for transition probabilities

    # remove remaining -s from rounding errors
    for i in range(n):
        for j in range(len(l[i]) - 1, -1, -1):
            if l[i][j] == -1:
                del l[i][j]
                del q[i][j]

    # merge parts of list transitioning to same node
    for i in range(n):
        temp = l[i][-1]
        for j in range(len(l[i]) - 2, -1, -1):
            if l[i][j] == temp:
                del l[i][j]
                del q[i][j]
            else:
                temp = l[i][j]

    return l, [[round(i, 15) for i in j] for j in q]


# Given [a, b, c], returns [a, a+b, a+b+c]
def list_incr(iterable, func=operator.add):
    it = iter(iterable)
    total = next(it)
    yield total
    for element in it:
        total = func(total, element)
        yield total


# return second largest value in list
def max2(x):
    if len(x) < 2:
        return 0.
    y = list(copy.copy(x))
    y.remove(max(y))
    return max(y)


# Given node and uniform random variable, return random neighbor based on weight
def OneStepTransit(TranCumul, TranList, state, ran):
    i = bisect.bisect_left(TranCumul[state], ran)
    return TranList[state][i]


# perform CFTP and record clusters along the critical time (refer to paper for critical times)
def back_path_clustering(adj, TranList, TranCumul):
    u = []
    flag = 0  # algorithm is done
    interval = 0  # time
    clusterings = []  # lists of clusterings
    critical_times = []  # times when node clusters coalesce

    num_nodes = len(adj)
    nodes = range(num_nodes)
    while flag == 0:
        interval += 1  # increment time
        current_state = copy.deepcopy(nodes)  # reset current state
        w = np.random.uniform(0, 1, 1)  # new RV
        u.insert(0, w[0])

        # move chains interval number of times according to RVs in u
        for k in range(0, interval):
            current_state = copy.deepcopy(list(map(lambda x: OneStepTransit(TranCumul, TranList, x, u[k]),
                                                   current_state)))
        # on first iteration
        if interval == 1:
            A = list(enumerate(current_state))  # (chain number, current node location)
            AA = set(current_state)  # nodes currently occupied by chains
            critical_times.append(interval)  # first time is critical time
            temp0 = []
            # generate list of clusterings
            for v in AA:
                temp0.append([indx for (indx, cr) in A if cr == v])
            clusterings.insert(0, temp0)

        # on subsequent iterations
        else:
            # some values from previous iteration
            recent_cluster = copy.deepcopy(clusterings[-1])
            recent_cluster_index = list(range(len(recent_cluster)))
            temp = []

            # find clusters where chains are also clustered by current state
            # chains clustered in recent_cluster must all move to same state in current_state to merge with any other
            # clusters
            for i in recent_cluster_index:
                if len(set([current_state[j] for j in recent_cluster[i]])) == 1:
                    temp.append((i, list(set([current_state[j] for j in recent_cluster[i]]))[0]))

            Z = collections.Counter(list(map(lambda x: itemgetter(1)(x), temp)))
            final_values = [a for (a, b) in Z.items() if
                            b >= 2]  # states to merge (b>=2 because need 2 clusters to merge)

            # check partial coalescence condition and merge if okay
            equal_count_indicator = [] * len(final_values)
            clusterings.append([])
            for r in final_values:

                clusters_coalesced = filter(lambda x: x[1] == r, temp)  # clusters to merge
                clusters_coalesced_index = list(map(lambda x: itemgetter(0)(x), clusters_coalesced))

                G_index = list(itertools.chain(*[recent_cluster[x] for x in clusters_coalesced_index]))
                G_state = copy.deepcopy(G_index)
                current_G_state = copy.deepcopy(G_state)

                # count occurrences of each chain in set of states who's chains are partially coalescing
                mycount = [1] * len(current_G_state)
                for k in range(0, interval):

                    current_G_state = copy.deepcopy(list(map(lambda x: OneStepTransit(TranCumul, TranList, x, u[k]),
                                                             current_G_state)))

                    for j in range(len(current_G_state)):
                        if current_G_state[j] in G_state:
                            mycount[j] += 1

                # each chain must have same number of occurrences in partially coalescing cluster
                equal_count_indicator.append(mycount.count(mycount[0]) == len(mycount))

                # merge new clusters
                temp2 = []
                if equal_count_indicator[-1]:
                    for s in clusters_coalesced_index:
                        temp2.append(recent_cluster[s])
                        recent_cluster_index.remove(s)
                    temp2 = list(itertools.chain(*temp2))
                    clusterings[-1].append(temp2)

            # unchanged clusters
            for r in recent_cluster_index:
                clusterings[-1].append(recent_cluster[r])
            del clusterings[0]

            # update if any changes to clustering
            if any(equal_count_indicator):
                critical_times.append(interval)  # save critical time

        user_coal_index = (len(set(current_state)) == 1)  # all chains coalesce

        # terminate algorithm
        if interval - critical_times[-1] >= 100 or user_coal_index:
            flag = 1

    # TODO: return single "best" clustering

    return clusterings, critical_times


# Given number of nodes, adjacency matrix, and clustering, return edit cost
def cluster_cost(adj: list, cluster: list):
    num_nodes = len(adj)
    induced_graph = np.zeros((num_nodes, num_nodes))
    for w in cluster:
        if len(w) > 1:
            for e in itertools.combinations(w, 2):
                induced_graph[e[0], e[1]] = 1
                induced_graph[e[1], e[0]] = 1
    return 0.5 * (np.sum(np.not_equal(adj, induced_graph)))
