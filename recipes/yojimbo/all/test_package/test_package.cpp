#include <iostream>
#include <yojimbo/reliable.h>
#include <yojimbo/serialize.h>
#include <yojimbo/tlsf.h>
#include <yojimbo/yojimbo.h>

using namespace yojimbo;

int main() {
  if (!InitializeYojimbo()) {
    std::cout << "Failed to initialize Yojimbo!\n";
    return 1;
  }

  std::cout << "Succesfully initialized Yojimbo\n";

  reliable_log_level(1);

  ShutdownYojimbo();

  return 0;
}
