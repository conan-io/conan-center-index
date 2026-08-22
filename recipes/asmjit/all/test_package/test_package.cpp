#include <iostream>

#include "asmjit/asmjit.h"

int main(int argc, char* argv[]) {
  asmjit::JitRuntime rt;
  asmjit::CodeHolder code;
  code.init(rt.environment());

  std::cout <<
    unsigned((ASMJIT_LIBRARY_VERSION >> 16)) << "." <<
    unsigned((ASMJIT_LIBRARY_VERSION >>  8) & 0xFF) << "." <<
    unsigned((ASMJIT_LIBRARY_VERSION      ) & 0xFF) << "\n";

  return 0;
}
