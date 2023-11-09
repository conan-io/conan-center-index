#include <iostream>

#include <openE57/openE57.h>

using namespace e57;
using namespace std;

int main() {
    E57Utilities utilities{};

    int astmMajor{0};
    int astmMinor{0};
    ustring libraryId{};
    utilities.getVersions(astmMajor, astmMinor, libraryId);

    std::cout << "E57 Version: " << astmMajor << "." << astmMinor << " - Library ID: " << libraryId
              << std::endl;

    return 0;
}
