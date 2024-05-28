#include <cstdio>
#if defined(FASTGLTF_0_7_0_LATER)
#  include <fastgltf/core.hpp>
#elif defined(FASTGLTF_0_5_0_LATER)
#  include <fastgltf/parser.hpp>
#else
#  include <fastgltf_parser.hpp>
#endif

#include <thread>
#include <chrono>

int main() {
#ifdef FASTGLTF_0_5_0_LATER
    // gcc < 11 uses pthread_once for std::call_once.
    // there is an known bug about pthread_once with older glibc.
    // This is workaround for that.
    // see: https://gcc.gnu.org/bugzilla/show_bug.cgi?id=60662
    std::this_thread::sleep_for(std::chrono::milliseconds(1));
#endif

    fastgltf::Parser parser;
    printf("Version: " FASTGLTF_QUOTE(FASTGLTF_VERSION) "\n");
    printf("C++17: " FASTGLTF_QUOTE(FASTGLTF_CPP_17) "\n");
    printf("C++20: " FASTGLTF_QUOTE(FASTGLTF_CPP_20) "\n");
}
