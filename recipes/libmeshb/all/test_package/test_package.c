#include "libmeshb7.h"

#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    int64_t LibIdx;
    int i, ver, dim, NmbVer, NmbTri, (*Nodes)[4], *Domains;
    float (*Coords)[3];

    // Open the mesh file for reading
    LibIdx = GmfOpenMesh( "test", GmfRead, &ver, &dim );

    // Get the number of vertices and triangles
    NmbVer = GmfStatKwd( LibIdx, GmfVertices  );
    NmbTri = GmfStatKwd( LibIdx, GmfTriangles );

    // Allocate memory accordingly
    Nodes   = malloc( NmbTri * 4 * sizeof(int)   );
    Coords  = malloc( NmbVer * 3 * sizeof(float) );
    Domains = malloc( NmbVer     * sizeof(int)   );

    // Move the file pointer to the vertices keyword
    GmfGotoKwd( LibIdx, GmfVertices );

    // Close the mesh file !
    GmfCloseMesh( LibIdx );

    return EXIT_SUCCESS;
}
