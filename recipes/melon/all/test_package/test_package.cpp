#include "melon/algorithm/bidirectional_dijkstra.hpp"
#include "melon/utility/static_digraph_builder.hpp"
#include "melon/container/static_digraph.hpp"

using namespace fhamonic::melon;

// test_package with bidirectional dijkstra because it condenses range-v3 uses
// shown to overwhelm some compilers

int main(int argc, char *argv[])
{
    static_digraph_builder<static_digraph, int> builder(6);

    builder.add_arc(0u, 1u, 7);  // 0
    builder.add_arc(0u, 2u, 9);  // 1
    builder.add_arc(0u, 5u, 14); // 2
    builder.add_arc(1u, 0u, 7);  // 3
    builder.add_arc(1u, 2u, 10); // 4
    builder.add_arc(1u, 3u, 15); // 5
    builder.add_arc(2u, 0u, 9);  // 6
    builder.add_arc(2u, 1u, 10); // 7
    builder.add_arc(2u, 3u, 12); // 8
    builder.add_arc(2u, 5u, 2);  // 9
    builder.add_arc(3u, 1u, 15); // 10
    builder.add_arc(3u, 2u, 12); // 11
    builder.add_arc(3u, 4u, 6);  // 12
    builder.add_arc(4u, 3u, 6);  // 13
    builder.add_arc(4u, 5u, 9);  // 14
    builder.add_arc(5u, 0u, 14); // 15
    builder.add_arc(5u, 2u, 2);  // 16
    builder.add_arc(5u, 4u, 9);  // 17

    auto [graph, length_map] = builder.build();

    bidirectional_dijkstra alg(graph, length_map, 0u, 3u);

    int dist = alg.run();
    if (dist != 21) return EXIT_FAILURE;

    if (!alg.path_found()) return EXIT_FAILURE;
    auto path = alg.path();
    if (std::ranges::distance(path) != 2) return EXIT_FAILURE;
    if (std::ranges::find(path, 1u) == path.end()) return EXIT_FAILURE;
    if (std::ranges::find(path, 8u) == path.end()) return EXIT_FAILURE;

    return EXIT_SUCCESS;
}
