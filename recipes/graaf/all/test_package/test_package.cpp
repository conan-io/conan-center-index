#include <graaflib/graph.h>

int main()
{
    graaf::directed_graph<const char, int> g;

    const auto a = g.add_vertex('a');
    const auto b = g.add_vertex('b');
    const auto c = g.add_vertex('c');

    g.add_edge(a, b, 1);
    g.add_edge(a, c, 1);

    return 0;
}
