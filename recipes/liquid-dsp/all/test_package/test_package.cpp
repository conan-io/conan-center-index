#include "liquid/liquid.h"

#include <iostream>

int main(int argc, char **argv)
{
  std::cout << liquid_libversion();
  return 0;
}
