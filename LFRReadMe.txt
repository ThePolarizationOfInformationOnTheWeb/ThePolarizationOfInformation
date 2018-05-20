To generate a stochastic block model and run the algorithm on it, run the function sbm in the python code with the appropriate inputs.

To generate an lfr model and run the algorithm on it, do the following:
    cd benchmark_2_1
    vi parameters.dat
    (modify the parameters accordingly)
    ./lfr.sh
This will create a new folder benchmark_2_1/graphx, where x is the next unused integer, with the lfr files.
Then run the function lfr in the python code with the correct path to the folder


The code will create a new file outputy.txt that includes the following:
-critical times and costs
-optimal cost and time
-correct clusters and recovered clusters
In the folder AnimFigs will be a circular drawing of the clusters at each critical time.