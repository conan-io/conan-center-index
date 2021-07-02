#include "graph.hh"

#include <cstdio>

int main() {
    bliss::Graph graph(4);

    graph.change_color(1, 1);

    graph.add_edge(0, 1);
    graph.add_edge(3, 0);
    graph.add_edge(1, 2);
    graph.add_edge(1, 3);
    graph.add_edge(2, 3);

    graph.write_dot(stdout);
    fprintf(stdout, "===\n");
    graph.write_dimacs(stdout);

    return 0;
}
