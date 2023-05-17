#include <graph.hh>

#include <fstream>
#include <iostream>

int main() {
    bliss::Graph graph(4);

    graph.change_color(1, 1);

    graph.add_edge(0, 1);
    graph.add_edge(3, 0);
    graph.add_edge(1, 2);
    graph.add_edge(1, 3);
    graph.add_edge(2, 3);

    graph.write_dot("dot_output.txt");
    std::ifstream ifs("dot_output.txt", std::ios::binary);
    std::cout << ifs.rdbuf() << std::endl;

    return 0;
}
