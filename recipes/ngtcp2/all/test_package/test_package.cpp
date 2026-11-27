#include <ngtcp2/ngtcp2.h>

#include <cstdio>
#include <cstdlib>

int main() {
    auto info = ngtcp2_version(0);
    std::printf("ngtcp2  headers: %s, library: %s (0x%06x)\n", NGTCP2_VERSION, info->version_str,
    info->version_num);
    std::printf("QUIC v1 supported: %s\n", ngtcp2_is_supported_version(NGTCP2_PROTO_VER_V1) ? "yes" : "no");
    return 0;
}
