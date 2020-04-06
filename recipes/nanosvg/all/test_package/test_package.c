#include <stdio.h>
#define NANOSVG_IMPLEMENTATION
#include <nanosvg.h>


int main(int argc, char **argv) {
  if (argc < 2) {
    fprintf(stderr, "Need at least one argument\n");
    return 1;
  }

  struct NSVGimage *image = nsvgParseFromFile(argv[1], "px", 96);
  printf("size: %f x %f\n", image->width, image->height);
  nsvgDelete(image);

  return 0;
}
