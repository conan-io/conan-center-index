#include "ZenLib/Utils.h"

#include <cstdint>
#include <iostream>

int main() {
    const std::uint8_t data[8] = {0xde, 0xad, 0xbe, 0xef, 0xca, 0xfe, 0xba, 0xbe};
    std::uint64_t be64 = ZenLib::BigEndian2int64u(data);
    std::uint64_t le64 = ZenLib::LittleEndian2int64u(data);

    if (be64 != 0xdeadbeefcafebabeULL) {
        std::cerr << "BigEndian incorrect! Got 0x" << std::hex << be64 << "\n";
        return 1;
    }

    if (le64 != 0xbebafecaefbeaddeULL) {
        std::cerr << "LittleEndian incorrect! Got 0x" << std::hex << le64 << "\n";
        return 1;
    }

    std::cout << "path separator on this platform is '";
#ifdef UNICODE
    std::wcout << ZenLib::PathSeparator;
#else
    std::cout << ZenLib::PathSeparator;
#endif
    std::cout << "'\n";
}
