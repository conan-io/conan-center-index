#include "avx512-32bit-qsort.hpp"

#include <array>
#include <string>

int main(int argc, const char *argv[]) {
    // If we attempt to call avx512_qsort on CPUs that don't have AVX512 instruction support,
    // the program will crash. Therefore, this test only checks that the header is found and can be compiled.
    if (argc == 2 && argv[1] == std::string("--has-avx512")) {
        std::array<float, 4> a { 7.4f, 3.1f, 2.2f, -9.3f };
        avx512_qsort<float>(a.data(), a.size());
    }
    return 0;
}
