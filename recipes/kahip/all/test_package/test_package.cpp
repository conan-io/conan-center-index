#include <iostream>
#include <sstream>

#include "kaHIP_interface.h"


int main(int argn, char **argv) {

    std::cout <<  "partitioning graph from the manual"  << std::endl;

    int n            = 5;
    int* xadj        = new int[6];
    xadj[0] = 0; xadj[1] = 2; xadj[2] = 5; xadj[3] = 7; xadj[4] = 9; xadj[5] = 12;

    int* adjncy      = new int[12];
    adjncy[0]  = 1; adjncy[1]  = 4; adjncy[2]  = 0; adjncy[3]  = 2; adjncy[4]  = 4; adjncy[5]  = 1; 
    adjncy[6]  = 3; adjncy[7]  = 2; adjncy[8]  = 4; adjncy[9]  = 0; adjncy[10] = 1; adjncy[11] = 3; 
    
    double imbalance = 0.03;
    int* part        = new int[n];
    int edge_cut     = 0;
    int nparts       = 2;
    int* vwgt        = NULL;
    int* adjcwgt     = NULL;

    kaffpa(&n, vwgt, xadj, adjcwgt, adjncy, &nparts, &imbalance, false, 0, ECO, & edge_cut, part);

    std::cout <<  "edge cut " <<  edge_cut  << std::endl;

    return 0;
}