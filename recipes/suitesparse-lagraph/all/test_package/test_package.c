#include <LAGraph.h>

int main (void)
{
    // initialize LAGraph
    char msg [LAGRAPH_MSG_LEN] ;
    LAGraph_Init (msg) ;
    GrB_Matrix A = NULL ;
    GrB_Vector centrality = NULL ;
    LAGraph_Graph G = NULL ;

    // read a Matrix Market file from stdin and create a graph
    LAGraph_MMRead (&A, stdin, msg) ;
    LAGraph_New (&G, &A, LAGraph_ADJACENCY_UNDIRECTED, msg) ;

    // compute the out-degree of every node
    LAGraph_Cached_OutDegree (G, msg) ;

    // compute the pagerank
    int niters = 0 ;
    LAGr_PageRank (&centrality, &niters, G, 0.85, 1e-4, 100, msg) ;

    // print the result
    LAGraph_Vector_Print (centrality, LAGraph_COMPLETE, stdout, msg) ;

    // free the graph, the pagerank, and finish LAGraph
    LAGraph_Delete (&G, msg) ;
    GrB_free (&centrality) ;
    LAGraph_Finalize (msg) ;
}
