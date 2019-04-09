import numpy as np
from EESpring19.Information import *

print('Creating Test Distributions')
dist1 = np.array([0.5,0.2,0.2,0.1])
dist2 = np.array([0.1,0.3,0.4,0.2])
print(dist1)
print(dist2)
print('Calculating Entropy of dist1')
distEnt = entropy(dist1)
print(distEnt)
print('Calculating KL Divergence of Distributions')
kl = kl_divergence(dist1,dist2)
print(kl)
print('Creating Sample Joint Distribution')
joint = np.array([[0.1,0.1,0.1,0.2],[0,0.1,0.1,0],[0,0.1,0.1,0],[0,0,0.1,0]])
print(joint)
print('Calculating Mutual Information')
mutual = mutual_information(joint,dist1,dist2)
print(mutual)