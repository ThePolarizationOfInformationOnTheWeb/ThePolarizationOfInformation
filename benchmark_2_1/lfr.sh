#change to edit parameter file according to editparam.py
#make and benchmark
#create new directory
#move files to new directory
#repeat for all parameters


echo "generating lfr files"

make
./benchmark

c=0
while [ -d "graph${c}" ]; do
	((c++))
done

echo "making directory graph${c}"

mkdir graph${c}

echo "moving files"

cp parameters.dat graph${c}/parameters.dat
cp network.dat graph${c}/network.dat
cp community.dat graph${c}/community.dat
cp statistics.dat graph${c}/statistics.dat

echo "all done"
