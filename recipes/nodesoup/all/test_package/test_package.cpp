#include "nodesoup.hpp"

#include <iostream>
#include <vector>

int main() {
    nodesoup::adj_list_t adjlist = {
        {0, 1},
        {1, 2},
        {2, 0},
        {0, 3},
        {3, 2},
        {2, 0},
    };

    auto print_points = [](const auto &points) {
        for(auto pnt: points) {
            std::cout << '(' << pnt.x << ',' << pnt.y << "),";
        }
    };

    auto callback = [&](const auto &points, int nb) {
        std::cout << "callback: " << nb << ' ';
        print_points(points);
        std::cout << "\n";
    };

    auto points = nodesoup::fruchterman_reingold(adjlist, 3, 3, 300, 15., callback);

    std::cout << "finish: ";
    print_points(points);
    std::cout << '\n';
}
