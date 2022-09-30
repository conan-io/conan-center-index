#include <cstdlib>
#include <iostream>

#include "package/foobar.hpp"

int main(void) {
  std::cout << "Create a minimal usage for the target project here.\n"
               "Avoid big examples, bigger than 100 lines.\n"
               "Avoid networking connections.\n"
               "Avoid background apps or servers.\n"
               "The propose is testing the generated artifacts only.\n";

  foobar.print_version();

  return EXIT_SUCCESS;
}
