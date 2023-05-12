#include <ogdf/basic/graph_generators.h>
#include <ogdf/layered/DfsAcyclicSubgraph.h>
#include <ogdf/fileformats/GraphIO.h>

using namespace ogdf;

int main()
{
	Graph G;
	randomSimpleGraph(G, 10, 20);

	DfsAcyclicSubgraph DAS;
	DAS.callAndReverse(G);

	GraphIO::write(G, "output-acyclic-graph.graphml", GraphIO::writeGraphML);

	return 0;
}
