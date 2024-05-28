#include <memory>

#include "CXXGraph/CXXGraph.hpp"

int main() {
  CXXGraph::Node<int> node0("0", 0);
  CXXGraph::Node<int> node1("1", 1);
  CXXGraph::Node<int> node2("2", 2);
  CXXGraph::Node<int> node3("3", 3);

  CXXGraph::UndirectedWeightedEdge<int> edge1(1, node1, node2, 2.0);
  CXXGraph::UndirectedWeightedEdge<int> edge2(2, node2, node3, 2.0);
  CXXGraph::UndirectedWeightedEdge<int> edge3(3, node0, node1, 2.0);
  CXXGraph::UndirectedWeightedEdge<int> edge4(4, node0, node3, 1.0);

  CXXGraph::T_EdgeSet<int> edgeSet;
  edgeSet.insert(std::make_shared<CXXGraph::UndirectedWeightedEdge<int>>(edge1));
  edgeSet.insert(std::make_shared<CXXGraph::UndirectedWeightedEdge<int>>(edge2));
  edgeSet.insert(std::make_shared<CXXGraph::UndirectedWeightedEdge<int>>(edge3));
  edgeSet.insert(std::make_shared<CXXGraph::UndirectedWeightedEdge<int>>(edge4));

  // Can print out the edges for debugging
  std::cout << edge1 << "\n";
  std::cout << edge2 << "\n";
  std::cout << edge3 << "\n";
  std::cout << edge4 << "\n";

  CXXGraph::Graph<int> graph(edgeSet);
  auto res = graph.dijkstra(node0, node2);

  std::cout << "Dijkstra Result: " << res.result << "\n";

  return 0;
}
