#include <libelfin/elf/elf++.hh>
#include <iostream>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

int
main(int argc, char** argv)
{
    using elf::to_string;

    int      fd = open(argv[1], O_RDONLY);
    elf::elf f(elf::create_mmap_loader(fd));

    auto& hdr = f.get_hdr();
    std::cout << "ELF Header:\n";
    std::cout << "  Magic: " << std::hex;
    for (auto c : hdr.ei_magic)
        std::cout << ' ' << static_cast<int>(c);
    std::cout << '\n';
    std::cout << "  Class:       " << to_string(hdr.ei_class) << '\n';
    std::cout << "  Data:        " << to_string(hdr.ei_data) << '\n';
    std::cout << "  Version:     " << static_cast<int>(hdr.ei_version) << '\n';
    std::cout << "  OS/ABI:      " << to_string(hdr.ei_osabi) << '\n';
    std::cout << "  ABI Version: " << static_cast<int>(hdr.ei_abiversion) << '\n';
    std::cout << "  Type:        " << to_string(hdr.type) << '\n';

    return 0;
}
