#include "gc.h"

#include <assert.h>
#include <stdio.h>

int main()
{
  GC_INIT();
  printf("BDWGC Version: %d", GC_get_version());
  GC_deinit();
  return 0;
}
