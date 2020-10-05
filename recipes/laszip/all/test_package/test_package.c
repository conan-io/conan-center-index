#include <laszip/laszip_api.h>

#include <stdio.h>

int main() {
  laszip_U8 version_major, version_minor;
  laszip_U16 version_revision;
  laszip_U32 version_build;
  laszip_get_version(&version_major, &version_minor, &version_revision, &version_build);
  printf("LASzip version %u.%u.%u - build %u\n", version_major, version_minor, version_revision, version_build);

  return 0;
}
