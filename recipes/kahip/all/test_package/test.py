import kahip

#build adjacency array representation of the graph
xadj           = [0,2,5,7,9,12]
adjncy         = [1,4,0,2,4,1,3,2,4,0,1,3]
vwgt           = [1,1,1,1,1]
adjcwgt        = [1,1,1,1,1,1,1,1,1,1,1,1]
supress_output = 0
imbalance      = 0.03
nblocks        = 2 
seed           = 0

# set mode 
#const int FAST           = 0;
#const int ECO            = 1;
#const int STRONG         = 2;
#const int FASTSOCIAL     = 3;
#const int ECOSOCIAL      = 4;
#const int STRONGSOCIAL   = 5;
mode = 0 

edgecut, blocks = kahip.kaffpa(vwgt, xadj, adjcwgt, 
                              adjncy,  nblocks, imbalance, 
                              supress_output, seed, mode)

print(edgecut)
print(blocks)