#include <graphthewy/GraphthewyModel.hpp>
#include <graphthewy/GraphthewyCycle.hpp>

int main(int argc, char** arvg)
{
    graphthewy::UndirectedGraph<int>(g);
    g.addVertex(1);
    g.addVertex(2);
    g.addVertex(3);
    g.link(1, 2);
    g.link(2, 3);
    g.link(3, 1);

    graphthewy::GraphCycle<graphthewy::UndirectedGraph, int>gc(g);

    return (gc.hasCycle() == true ? 0 : -1);
}
