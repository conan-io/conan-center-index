#include <cstdio>

#include <cloudini_lib/cloudini.hpp>

int main() {
    // Force a link-time reference to a non-inline symbol defined in
    // src/codec_common.cpp, proving the library is correctly linked.
    std::printf(
        "cloudini test_package: ToString(ZSTD) = %s\n",
        Cloudini::ToString(Cloudini::CompressionOption::ZSTD));
    return 0;
}
