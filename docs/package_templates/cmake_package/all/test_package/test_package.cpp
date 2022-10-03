#include <cstdlib>
#include <iostream>

#include "package/foobar.hpp"

int main(void) {
  std::cout << "Create a minimal usage sample for the target project here.\n"
               "Avoid examples longer than 100 lines.\n"
               "Avoid network connections.\n"
               "Avoid background apps or servers.\n"
               "The purpose is to test the generated artifacts only.\n";

  foobar.print_version();

  return EXIT_SUCCESS;
}
