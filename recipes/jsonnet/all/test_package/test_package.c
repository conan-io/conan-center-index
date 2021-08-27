#include <libjsonnet.h>

#include <stdio.h>

int main() {
  struct JsonnetVm* vm = jsonnet_make();
  jsonnet_max_stack(vm, 10);
  printf("%s\n", jsonnet_version());
  return 0;
}

