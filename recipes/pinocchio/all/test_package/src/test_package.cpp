#include <vector>
#include <string>
#include "pinocchio/utils/file-explorer.hpp"

int main()
{
   std::vector<std::string> paths;
   pinocchio::extractPathFromEnvVar("CONAN_PINOCCHIO_TEST_PACKAGE_UNUSED_VAR",
                                    paths, ";");
}
