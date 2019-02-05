#work in progress

#write parameters corresponding to given integer to parameters.dat file
#[numnodes, avgdeg, maxdeg, degdistrexp, commsizeexp, mixparam, mincommsize, maxcommsize], last two optional
import sys

gnum = int(sys.argv[1])

#run following parameters 
param = 2*[[2000, 20, 200, 1.5, 1, 0.2, 20, 1000]] +\
        2*[[5000, 20, 200, 1.5, 1, 0.2, 20, 1000]]
            
descr = ['number of nodes', 'average degree', 'maximum degree',
         'exponent for the degree distribution', 'exponent for the community size distribution',
         'mixing parameter', 
         'minimum for the commmunity sizes (optional; just comment this line, if you wish)',
         'maximum for the community sizes (optional; just comment this line, if you wish)']

param_num = len(descr)
text = 79*'#'+'\n'+79*'#'+'\n'
for pnum in range(param_num):
    text += str(param[gnum][pnum])+'\t#'+descr[pnum]+'\n'
text += 79*'#'+'\n'+79*'#'+'\n'

with open('parameters.dat', 'wb') as f:
    f.write(text)
 
