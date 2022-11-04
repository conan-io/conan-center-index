#include <ghc/filesystem.hpp>
#include <iostream>

int main(int argc, char** argv) {
    std::cout << "Version: " << GHC_FILESYSTEM_VERSION << std::endl;
    ghc::filesystem::path program{argv[0]};
    std::cout << "Program: " << ghc::filesystem::absolute(program) << std::endl;
    return 0;
}
