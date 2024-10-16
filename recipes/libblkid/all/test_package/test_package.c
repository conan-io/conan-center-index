#include <stddef.h>

#include <blkid/blkid.h>
#include <stdlib.h>

int main()
{
  if (blkid_get_library_version(NULL, NULL) <= 0) {
    return EXIT_FAILURE;
  }
  return EXIT_SUCCESS;
}
