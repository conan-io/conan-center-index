#include <GraphBLAS.h>

int main() {
  GrB_Index const NUM_NODES = 3;
  GrB_Index const NUM_EDGES = 4;
  GrB_Index row_indices[] = {0, 1, 1, 2};
  GrB_Index col_indices[] = {1, 0, 2, 1};
  bool values[] = {true, true, true, true};
  GrB_Matrix graph;
  GrB_Matrix_new(&graph, GrB_BOOL, NUM_NODES, NUM_NODES);
  GrB_Matrix_build(graph, row_indices, col_indices, (bool *)values, NUM_EDGES, GrB_LOR);
}
