#include <libjsonnet++.h>
#include <libjsonnet.h>

#include <iostream>

int main() {
  // C++ library
  jsonnet::Jsonnet j;
  if (!j.init()) {
    return 1;
  }
  std::cout << jsonnet::Jsonnet::version() << "\n";

  // C library
  struct JsonnetVm* vm = jsonnet_make();
  jsonnet_max_stack(vm, 10);
  std::cout << jsonnet_version() << "\n";
  return 0;
}
