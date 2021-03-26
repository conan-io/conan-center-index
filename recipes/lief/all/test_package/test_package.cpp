#include <cstdlib>
#include <iostream>

#include "LIEF/LIEF.hpp"
#include "LIEF/version.h"

int main(int argc, char **argv)
{
    if (argc < 2) {
        std::cerr << "Need at least one argument\n" << std::endl;
        return 1;
    }

    std::cout << LIEF_NAME << HUMAN_VERSION << std::endl;

#if defined(_WIN32)
    std::unique_ptr<LIEF::PE::Binary> pe = LIEF::PE::Parser::parse(argv[1]);
#elif defined(__linux__)
    std::unique_ptr<LIEF::ELF::Binary> elf = LIEF::ELF::Parser::parse(argv[1]);
#elif defined(__APPLE__)
    std::unique_ptr<LIEF::MachO::FatBinary> macho = LIEF::MachO::Parser::parse(argv[1]);
#else
    #warning "Non efficient test."
#endif

    return EXIT_SUCCESS;
}
