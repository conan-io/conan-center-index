#include <iostream>
#include "assimp/version.h"
#include "assimp/Importer.hpp"

int main() {
    Assimp::Importer importer;
    std::cout << "Assimp version " << aiGetVersionMajor() << "." << aiGetVersionMinor() << "." << aiGetVersionRevision() << std::endl;
}
