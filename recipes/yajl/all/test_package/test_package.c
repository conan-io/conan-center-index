#include <yajl/yajl_gen.h>
#include <yajl/yajl_version.h>
#include <stdio.h>
#include <stdlib.h>

#define CHK(x) if (x != yajl_gen_status_ok) return 1;

int main(void) {
  printf("Welcome to YAJL v%d.%d.%d!", YAJL_MAJOR, YAJL_MINOR, YAJL_MICRO);
  yajl_gen yg;
  yajl_gen_status s;

  yg = yajl_gen_alloc(NULL);
  CHK(yajl_gen_map_open(yg));
  CHK(yajl_gen_map_close(yg));
  s = yajl_gen_map_close(yg);

  return yajl_gen_generation_complete == s ? EXIT_SUCCESS : EXIT_FAILURE;
}
