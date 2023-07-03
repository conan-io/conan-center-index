#include <cstdio>
#ifdef FASTGLTF_0_5_0_LATER
#  include <fastgltf/parser.hpp>
#else
#  include <fastgltf_parser.hpp>
#endif

int main() {
    fastgltf::Parser parser;
    printf("Version: " FASTGLTF_QUOTE(FASTGLTF_VERSION) "\n");
    printf("C++17: " FASTGLTF_QUOTE(FASTGLTF_CPP_17) "\n");
    printf("C++20: " FASTGLTF_QUOTE(FASTGLTF_CPP_20) "\n");
}
