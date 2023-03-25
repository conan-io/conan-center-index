#include <cstdio>
#include <fastgltf_parser.hpp>

int main() {
    fastgltf::Parser parser;
    printf("Version: " FASTGLTF_QUOTE(FASTGLTF_VERSION));
    printf("C++17: " FASTGLTF_QUOTE(FASTGLTF_CPP_17));
    printf("C++20: " FASTGLTF_QUOTE(FASTGLTF_CPP_20));
}
