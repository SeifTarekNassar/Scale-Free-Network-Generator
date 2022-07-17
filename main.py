"""
Created on Thu May  5 11:38:54 2022
for assignment one Topologies module
@author: Seif TK (Cabel)
"""

import random as rnd
import matplotlib.pyplot as plotf
import networkx as netX
import collections
import operator
import powerlaw
from networkx import sigma, omega

nodes = []  # nodes array
areaSize = 500  # max size deployment area
numOfNodes = 500  # number of Nodes
radius = 195  # Radius of communication
Hnode = 100  # highest degree for node
percentOfEdges = 0.01  # percentage of total edges
intialNumberOfLinks = 1  # links with each new node


### colors
nodesColor = "#4287f5"  # blue color
hubsColor = "#f54242" # red color
generalGraphClr = "blue"  # dark blue

# function to sort values in the nodes
def sorti(n):
    return (sorted(nodes, key=lambda x: x[0]))  # sorting via 'x'
# Function to find distance between two nodes
def distance(i, j):
    x = abs(i[0] - j[0])
    y = abs(i[1] - j[1])
    d = (x ** 2 + y ** 2) ** (1 / 2)
    return d

# Function to identify neighbours of each nodes
def neighbour():
    nodes_nbr = {}  # dict of nbrs
    temp_nodes = nodes.copy()
    for i in nodes:
        temp_nbr = []
        for j in temp_nodes:
            if distance(i, j) < radius and j != i:
                temp_nbr.append(j)
        nodes_nbr[tuple(i)] = temp_nbr
        del temp_nbr
    return nodes_nbr
# function to generate node pairs
def generateNode():
    i = 0
    while i < numOfNodes:
        tempNode1 = rnd.randint(0, areaSize)
        tempNode2 = rnd.randint(0, areaSize)
        tempNodes = []
        tempNodes.append(tempNode1)
        tempNodes.append(tempNode2)
        if tempNodes not in nodes:
            nodes.append(tempNodes)
            i = i + 1
# NetworkX graph with only nodes (without any edges)
def generateGraph0(clr):
    G = netX.Graph()
    for i in nodes:
        G.add_node(tuple(i), pos=i)
    pos = netX.get_node_attributes(G, 'pos')
    netX.draw(G, pos, node_size=10, node_color=clr)
    plotf.title("the generated Graph with only nodes (without any edges)")
    plotf.ylabel("the generated Graph with only nodes (without any edges)")
    plotf.show()
    return G
def degreeboxplot(G, clr):
    degree_sequence = sorted([d for n, d in G.degree()], reverse=True)
    degreeCount = collections.Counter(degree_sequence)
    deg, cnt = zip(*degreeCount.items())
   # plotf.bar(deg, cnt, width=0.80, color=clr)
    plotf.loglog(deg, cnt, 'bo')
    plotf.title("Degree Histogram")
    plotf.ylabel("Count")
    plotf.xlabel("Degree")
    plotf.show()
def degreeHistogram(G, clr):
    degree_sequence = sorted([d for n, d in G.degree()], reverse=True)
    degreeCount = collections.Counter(degree_sequence)
    deg, cnt = zip(*degreeCount.items())
    plotf.bar(deg, cnt, width=0.80, color=clr)
    # plt.loglog(deg,cnt)
    plotf.title("Degree Histogram")
    plotf.ylabel("Count")
    plotf.xlabel("Degree")
    plotf.show()
# probability of each node's degree in resepect to WHOLE NETWORK
def perMap(G):
    per = []
    permap = {}
    temp = netX.degree(G)
    sum = 0
    for i in temp:
        sum = sum + i[1]
    if sum == 0:
        sum = 0.000000001
    for i in temp:
        if i[1] < Hnode:
            per.append(i[1] / sum)
        else:
            per.append(i[1] / (sum * i[1]))
    for i, j in zip(temp, per):
        permap[i[0]] = j
    return permap
def perMapRange(permap):
    # finding out ranges
    permaprange = {}
    prev = 0.0
    sorted_permap = dict(sorted(permap.items(), key=operator.itemgetter(1)))
    for keys in sorted_permap:
        t = []
        new = sorted_permap[keys]
        margin = 0.00001
        a = prev
        b = new + prev - margin
        if a == 0 and b < 0:
            t.append(0)
            t.append(0)
        else:
            t.append(a)
            t.append(b)
        permaprange[keys] = tuple(t)
        prev = new + prev
        del t
        # print(permaprange)
    return permaprange


def prefAttachment(G, seed, data):
    for ii in range(0, int(((numOfNodes * (numOfNodes - 1)) / 2) * percentOfEdges)):
        permap = perMap(G)  # prob map of each node wrt whole graph
        nbrs_seed = data[tuple(seed)]  # nbrs of the seed node
        new_permap = {}
        for i in nbrs_seed:
            new_permap[tuple(i)] = permap[tuple(i)]

        # first mapping permap to [0,1]
        permap_mapped = {}
        _sum = 0.0
        for keys in new_permap:
            _sum = _sum + new_permap[keys]
        if _sum == 0:
            _sum = 0.0000001
        for keys in new_permap:
            permap_mapped[keys] = (new_permap[keys] / _sum)

        _sum = 0
        for keys in permap_mapped:
            _sum = _sum + permap_mapped[keys]

        if _sum == 0:
            for jj in range(0, intialNumberOfLinks):
                rnd_nbr = tuple(rnd.choice(nbrs_seed))
                G.add_edge(rnd_nbr, tuple(seed))
            # print('Seed: {} --> rnd_nbr: {} \n'.format(seed,rnd_nbr))
        else:
            new_permaprange = perMapRange(permap_mapped)
            for jj in range(0, intialNumberOfLinks):
                select = rnd.uniform(0, 1)
                for keys in new_permaprange:
                    t = new_permaprange[keys]
                    if select >= t[0] and select <= t[1]:
                        G.add_edge(tuple(seed), keys)

        seed = rnd.choice(nbrs_seed)

    # Rewire
    final_degree = netX.degree(G)
    final_0nodes = []
    for keys in final_degree:
        if keys[1] == 0:
            final_0nodes.append(keys[0])
    for i in final_0nodes:
        nbr_i = data[tuple(i)]
        flag = 0
        while flag != 1:
            rnd_nbr_i = tuple(rnd.choice(nbr_i))
            if G.degree(rnd_nbr_i) != 0:
                G.add_edge(rnd_nbr_i, tuple(i))
                flag = 1

    permap = perMap(G)  # prob map of each node wrt whole graph
    return G


def findHubs(d):
    deg = []
    for i in d:
        deg.append(d[i])

    deg.sort()

    h = []
    for i in deg:
        if i > (deg[-1] / 2):
            h.append(i)

    hub = []
    for i in h:
        for j in d:
            if i == d[j]:
                hub.append(j)
    return hub


def showGraph(G):
    d = dict(netX.degree(G))

    hub = findHubs(d)

    node_color = []
    for node in G:
        if node in hub:
            node_color.append(hubsColor)
        else:
            node_color.append(nodesColor)

    pos = netX.get_node_attributes(G, 'pos')
    netX.draw(G, pos, node_size=[v * 10 for v in d.values()], node_color=node_color)
    plotf.title("Scale Free Network: Area {} X {}, Nodes: {}".format(areaSize, areaSize, numOfNodes))
    labeltext = "Hubs: " + hubsColor + " - Normal Nodes: " + nodesColor
    plotf.ylabel(labeltext)
    plotf.show()


def powerlawY(g):
    degrees = {}

    nodes = list(g.nodes)

    for node in nodes:
        key = len(list(g.neighbors(node)))
        degrees[key] = degrees.get(key, 0) + 1

    max_degree = max(degrees.keys(), key=int)
    num_nodes = []
    for i in range(1, max_degree + 1):
        num_nodes.append(degrees.get(i, 0))

    fit = powerlaw.Fit(num_nodes)
    print(fit.power_law.alpha)

def breakGraphRandomly(GC, RB):
    nodes = list(GC.nodes())
    i = 0
    while i<RB:
        x = tuple(rnd.choice(nodes))
        GC.remove_node(x)
        nodes.remove(x)
        i = i + 1
    #print('Number of nodes removed: {}'.format(i))
    return GC

# Robustness test
def robustnessTest(G):
        t = 0
        min_nLSG = 1000000000000
        for t in range(0, 1):
            GC = G.copy()
            breaks = 0
            nodes_LSG = 2
            worst_case_nLSG = []
            worst_case_br = []
            br = []
            nLSG = []
            while breaks <= numOfNodes and nodes_LSG > 1:
                Gd = breakGraphRandomly(GC, 1)
                LSG = (Gd.subgraph(c) for c in netX.connected_components(Gd))
                LSG = list(LSG)[0]
                nodes_LSG = len(LSG)
                breaks = breaks + 1
                br.append(breaks)
                nLSG.append(nodes_LSG)

            # Expanding
            br.append(numOfNodes)
            nLSG.append(1)

            if sum(nLSG) < min_nLSG:
                min_nLSG = sum(nLSG)
                worst_case_nLSG = nLSG
                worst_case_br = br

            diag = []
            d = 0
            while d <= numOfNodes:
                diag.append(d)
                d = d + 1

        plotf.plot(worst_case_br, worst_case_nLSG, 'r')
        diag_rev = diag.copy()
        diag_rev.reverse()
        plotf.plot(diag, diag_rev, 'b')

        plotf.title('Robustness of Algorithm')
        plotf.xlabel('Number of Random Breaks')
        plotf.ylabel('Number of nodes in  largest sub-graph')
        #show robustness plot
        plotf.show()


#############################################################################
generateNode()  # Calling function to generate nodes
nodePair = neighbour()  # Calling function generate node & neighbour pairs
G = generateGraph0(generalGraphClr)  # Calling function to generate graph

# Choosing a center element
pos = netX.get_node_attributes(G, 'pos')
r1 = areaSize * 0.35
r2 = areaSize * 0.55
center = []
for keys in pos:
    if keys[0] > r1 and keys[0] < r2 and keys[1] > r1 and keys[1] < r2:
        center.append(keys)
seed = rnd.choice(center)


G = prefAttachment(G, seed, nodePair)
showGraph(G)
degreeHistogram(G, 'red')
degreeboxplot(G, 'blue')


powerlawY(G)
robustnessTest(G)

# small world cofficent calculations
# small-world coefficient (sigma)
# Sigma = netX.sigma(G)
# print("The small-world coefficient (Sigma) of the graph ")
# print(Sigma)
# #The small-world coefficient (omega)
# Omega = netX.omega(G)
# print("The small-world coefficient (omega) of the graph")
# print(Omega)
