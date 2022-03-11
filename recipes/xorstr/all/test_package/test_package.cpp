#define JM_XORSTR_DISABLE_AVX_INTRINSICS
#include <xorstr.hpp>

#include <cstdio>

int main() {
    std::puts(xorstr_("an extra long hello_world"));
    return 0;
}
