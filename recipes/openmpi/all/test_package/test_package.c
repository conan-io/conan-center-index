#include <stdio.h>
#include <stdlib.h>

#include <mpi.h>

int main(int argc, char* argv[])
{
  char version[MPI_MAX_LIBRARY_VERSION_STRING] = {0};
  int len = 0;
  MPI_Get_library_version(version, &len);
  printf("MPI version: %s\n", version);
  return EXIT_SUCCESS;
}
