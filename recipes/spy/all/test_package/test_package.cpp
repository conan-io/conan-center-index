#include <iostream>
#include <spy/spy.hpp>

int main()
{
  std::cout << spy::operating_system      << std::endl;
  std::cout << spy::architecture          << std::endl;
  std::cout << spy::simd_instruction_set  << std::endl;
  std::cout << spy::compiler              << std::endl;
  std::cout << spy::libc                  << std::endl;
  std::cout << spy::stdlib                << std::endl;
}
