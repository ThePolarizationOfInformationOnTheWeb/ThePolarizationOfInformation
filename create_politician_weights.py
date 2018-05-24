import csv
import json

json_data=open("tweetdict.json").read()
dictionary = json.loads(json_data)

weightlist = []
indexlist = []
for itema in dictionary:
    itemaweights = []
    itemaindex = []
    b = 0
    maxaweight = 0
    for itemb in dictionary:
        if (itema != itemb):
            weight = set(dictionary[itema]) & set(dictionary[itemb])
            weight = len(weight)
            if (weight > maxaweight):
                maxaweight = weight
            itemaweights.append(weight)
            itemaindex.append(b)
        b = b + 1
    itemaweights = [float(a)/float(maxaweight) for a in itemaweights]
    weightlist.append(itemaweights)
    indexlist.append(itemaindex)

with open("politicianweightlist.txt", "w") as f:
    f.write(str(weightlist))

with open("politicianindexlist.txt", "w") as f:
    f.write(str(indexlist))
