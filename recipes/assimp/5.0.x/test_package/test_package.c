#include <stdio.h>

#include <assimp/cimport.h>
#include <assimp/scene.h>
#include <assimp/postprocess.h>

int main(int argc, char **argv) {
  if (argc < 2) {
    printf("Need at least one argument\n");
    return 1;
  }

  const C_STRUCT aiScene *scene = aiImportFile(argv[1],
    aiProcess_CalcTangentSpace       |
    aiProcess_Triangulate            |
    aiProcess_JoinIdenticalVertices  |
    aiProcess_SortByPType);

  if (!scene) {
    return 1;
  }

  aiReleaseImport(scene);

  return 0;
}
