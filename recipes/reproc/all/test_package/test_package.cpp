#include <reproc++/reproc.hpp>
#include <iostream>

int main()
{
  try {
    reproc::process process;
    reproc::options options;
    options.redirect.parent = true;
    std::cout << "reproc++ setup successful. Process object created.\n";
  } catch (const std::exception &e) {
    std::cerr << "Error: " << e.what() << '\n';
    return 1;
  }
  return 0;
}
