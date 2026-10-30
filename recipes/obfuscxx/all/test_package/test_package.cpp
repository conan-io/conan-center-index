#include <obfuscxx/obfuscxx.h>

#include <cstdlib>
#include <cstring>

int main() {
    return std::strcmp(obfxxs("test_package"), "test_package") == 0
        ? EXIT_SUCCESS
        : EXIT_FAILURE;
}