#include <openE57/openE57.h>
#include <iostream>

using namespace e57;
using namespace std;

int main(int /*argc*/, char** /*argv*/)
{
  E57Utilities utilities{};

  int     astmMajor{0};
  int     astmMinor{0};
  ustring libraryId{};
  utilities.getVersions(astmMajor, astmMinor, libraryId);

  std::cout << "E57 Version: " << astmMajor << "." << astmMinor << " - Library ID: " << libraryId << std::endl;

  return 0;
}
