#include <nxpp.hpp>

int main() {
    nxpp::GraphInt graph;
    graph.add_edge(0, 1, 2);
    return graph.has_edge(0, 1) ? 0 : 1;
}
