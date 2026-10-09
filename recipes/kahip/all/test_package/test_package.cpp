#include <iostream>
#include <vector>

#include "kaHIP_interface.h"

int main() {
    std::cout << "partitioning graph from the manual" << std::endl;

    int n = 5;
    std::vector<int> xadj = {0, 2, 5, 7, 9, 12};
    std::vector<int> adjncy = {1, 4, 0, 2, 4, 1, 3, 2, 4, 0, 1, 3};

    double imbalance = 0.03;
    std::vector<int> part(n);
    int edge_cut = 0;
    int nparts = 2;

    kaffpa(&n, nullptr, xadj.data(), nullptr, adjncy.data(), &nparts, &imbalance,
           false, 0, ECO, &edge_cut, part.data());

    std::cout << "edge cut " << edge_cut << std::endl;

    return 0;
}
