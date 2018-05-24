import csv

lines = []
with open("DataFiles/progressivetweets.csv", "r") as f:
    i = 0
    csvreader = csv.reader(f)
    for row in csvreader:
        if (i == 0):
            i = 1
        else:
            lines.append(row)

weightlist = []
indexlist = []
for itema in lines:
    itemaweights = []
    itemaindex = []
    b = 0
    for itemb in lines:
        if (itema != itemb):
            weight = float(itema[4]) - float(itemb[4])
            weight = 2 - abs(weight)
            weight = weight/2
            itemaweights.append(weight)
            itemaindex.append(b)
        b = b + 1
    weightlist.append(itemaweights)
    indexlist.append(itemaindex)

with open("DataFiles/allweightlist.txt", "w") as f:
    f.write(str(weightlist))

with open("DataFiles/allindexlist.txt", "w") as f:
    f.write(str(indexlist))
