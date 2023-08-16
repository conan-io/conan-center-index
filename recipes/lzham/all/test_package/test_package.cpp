#include <cstdlib>
#include <cstring>

#include <lzham_static_lib.h>

int main() {
    unsigned char in[] = "Hello Conan Center!";
    unsigned char out[sizeof(in)];

    lzham_z_stream stream;
    std::memset(&stream, 0, sizeof(stream));
    stream.next_in = in;
    stream.avail_in = sizeof(in);
    stream.next_out = out;
    stream.avail_out = sizeof(out);
    if (lzham_z_deflateInit(&stream, LZHAM_Z_BEST_COMPRESSION) != LZHAM_Z_OK)
        return EXIT_FAILURE;

    if (lzham_z_deflate(&stream, LZHAM_Z_FULL_FLUSH) != LZHAM_Z_OK)
        return EXIT_FAILURE;

    return EXIT_SUCCESS;
}
