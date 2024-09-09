#include "melon/algorithm/bidirectional_dijkstra.hpp"
#include "melon/utility/static_digraph_builder.hpp"
#include "melon/container/static_digraph.hpp"

using namespace fhamonic::melon;

int main(int argc, char * argv[]) {
    static_digraph_builder<static_digraph, int> builder(6);

    builder.add_arc(0u, 1u, 7);
    builder.add_arc(0u, 2u, 9);
    builder.add_arc(0u, 5u, 14);
    builder.add_arc(1u, 0u, 7);
    builder.add_arc(1u, 2u, 10);
    builder.add_arc(1u, 3u, 15);
    builder.add_arc(2u, 0u, 9);
    builder.add_arc(2u, 1u, 10);
    builder.add_arc(2u, 3u, 12);
    builder.add_arc(2u, 5u, 2);
    builder.add_arc(3u, 1u, 15);
    builder.add_arc(3u, 2u, 12);
    builder.add_arc(3u, 4u, 6);
    builder.add_arc(4u, 3u, 6);
    builder.add_arc(4u, 5u, 9);
    builder.add_arc(5u, 0u, 14);
    builder.add_arc(5u, 2u, 2);
    builder.add_arc(5u, 4u, 9);

    auto [graph, length_map] = builder.build();

    bidirectional_dijkstra alg(graph, length_map, 0u, 3u);

    return alg.run() == 21 ? EXIT_SUCCESS : EXIT_FAILURE;
}