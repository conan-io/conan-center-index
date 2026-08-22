#include <stdio.h>

#include <assimp/cimport.h>
#include <assimp/scene.h>
#include <assimp/postprocess.h>

int main(int argc, char **argv) {
  const C_STRUCT aiScene *scene = aiImportFile("",
    aiProcess_CalcTangentSpace       |
    aiProcess_Triangulate            |
    aiProcess_JoinIdenticalVertices  |
    aiProcess_SortByPType);

  aiReleaseImport(scene);

  return 0;
}
