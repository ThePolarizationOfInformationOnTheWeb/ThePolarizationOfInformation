from EESpring19.Clusterer import Clusterer
import pandas as pd
import numpy as np

print("Creating Adjaceny Matrix")
adj = pd.DataFrame(np.array([[0, 2, 1], [2, 0, 6], [1, 6, 0]]),columns=['a', 'b', 'c'])
print(adj)
print("Creating Clusterer Object")
clusterer = Clusterer(adj)
print("node_id_map")
print(clusterer.node_id_map)
print("updating clusterer")
#adj = pd.DataFrame(np.array([[0,0.5,3,5,5],[0.5,0,3,5,5],[3,3,0,3,3],[5,5,3,0,0.5],[5,5,3,0.5,0]]))
adj = pd.DataFrame(np.array([[1,1,0,0,0],[1,1,0,0,0],[0,0,1,1,1],[0,0,1,1,1],[0,0,1,1,1]]))
# adj = pd.DataFrame(np.array([[1,1,1,1,0,0,0,0,0],
#                              [1,1,1,1,0,0,0,0,0],
#                              [1,1,1,1,0,0,0,0,0],
#                              [1,1,1,1,1,0,0,0,0],
#                              [0,0,0,1,1,0.0402011,0,0,0],
#                              [0,0,0,0,0.0402011,1,1,1,1],
#                              [0,0,0,0,0,1,1,1,1],
#                              [0,0,0,0,0,1,1,1,1],
#                              [0,0,0,0,0,1,1,1,1]]))
#x = 0.02440051047
x=0.002
y = 0.04
z = 0.5
adj = pd.DataFrame(np.array([[z,y,y,y,x,0,0,0,0],
                             [y,z,y,y,x,0,0,0,0],
                             [y,y,z,y,x,0,0,0,0],
                             [y,y,y,z,x,0,0,0,0],
                             [x,x,x,x,z,x,x,x,x],
                             [0,0,0,0,x,z,y,y,y],
                             [0,0,0,0,x,y,z,y,y],
                             [0,0,0,0,x,y,y,z,y],
                             [0,0,0,0,x,y,y,y,z]]))
#adj = pd.DataFrame(np.array([[1,1,1,0,0],[1,1,0,0,0],[1,0,1,1,1],[0,0,1,1,1],[0,0,1,1,1]]))
clusterer.update_network(adj)
print(clusterer.adj)
print("Getting Clustering")
clustering = clusterer.get_clustering("backward_path", 'all')
print(clustering)
print("finish")