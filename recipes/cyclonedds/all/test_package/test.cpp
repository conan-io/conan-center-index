#include "dds/version.h"
#include <iostream>

int main(int argc, char *argv[]) {
  std::cout << std::endl
            << "--------------------------->Tests are "
               "done.<--------------------------"
            << std::endl
            << "CycloneDDS Using implementation: " << DDS_PROJECT_NAME
            << ", version: " << DDS_VERSION << std::endl
            << "///////////////////////////////////////////////////////////////"
               "///////"
            << std::endl;
  return 0;
}
