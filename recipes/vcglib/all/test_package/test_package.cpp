#include <vcg/complex/complex.h>
#include <wrap/io_trimesh/import.h>

#include <iostream>

class MyVertex;
class MyEdge;
class MyFace;

struct MyUsedTypes: public vcg::UsedTypes<vcg::Use<MyVertex>::AsVertexType, vcg::Use<MyEdge>::AsEdgeType, vcg::Use<MyFace>::AsFaceType>{};
class MyVertex: public vcg::Vertex<MyUsedTypes, vcg::vertex::Coord3f, vcg::vertex::Normal3f, vcg::vertex::BitFlags>{};
class MyFace: public vcg::Face<MyUsedTypes, vcg::face::FFAdj, vcg::face::VertexRef, vcg::face::BitFlags>{};
class MyEdge: public vcg::Edge<MyUsedTypes>{};
class MyMesh: public vcg::tri::TriMesh<std::vector<MyVertex>, std::vector<MyFace> , std::vector<MyEdge> >{};

int main(int argc, char **argv) {
    if (argc < 2) {
        std::cerr << "Need at least 1 argument" << std::endl;
        return -1;
    }

    MyMesh m;
    int dummymask = 0;
    if (vcg::tri::io::Importer<MyMesh>::Open(m, argv[1]) != 0) {
        std::cerr << "Error reading file " << argv[1] << std::endl;
        return -1;
    }

    vcg::tri::RequirePerVertexNormal(m);
    vcg::tri::UpdateNormal<MyMesh>::PerVertexNormalized(m);
    std::cout << "Mesh has " << m.VN() << " vert and " << m.FN() << " faces" << std::endl;

    return 0;
}
