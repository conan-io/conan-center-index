#include <stdio.h>
#include <openslide.h>


int main(int argc, char **argv) {
  printf ("openslide version: %s\n", openslide_get_version());
  return 0;
}
