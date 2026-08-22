#include <ode/ode.h>

int main()
{
    dInitODE();

    const int VertexCount = 4;
    const int IndexCount = 2 * 3;
    float vertices[12] = {
        -1,-1,0,
        1,-1,0,
        1,1,0,
        -1,1,0
    };
    dTriIndex indices[6] = {
        0,1,2,
        0,2,3
    };

    dTriMeshDataID data = dGeomTriMeshDataCreate();
    dGeomTriMeshDataBuildSingle(data,
                                vertices,
                                3 * sizeof(float),
                                VertexCount,
                                indices,
                                IndexCount,
                                3 * sizeof(dTriIndex));
    dGeomID trimesh = dCreateTriMesh(0, data, 0, 0, 0);
    const dReal radius = 4;
    dGeomID sphere = dCreateSphere(0, radius);
    dContactGeom cg[4];
    int nc;
    dVector3 trinormal = { 0, 0, -1 };

    dGeomSetPosition(sphere, 0,0,radius);
    nc = dCollide(trimesh, sphere, 4, &cg[0], sizeof cg[0]);

    dCloseODE();
    return 0;
}
