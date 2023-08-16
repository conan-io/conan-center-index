// Include the specific gzip headers your code needs, for example...
#include <gzip/compress.hpp>
#include <gzip/config.hpp>
#include <gzip/decompress.hpp>
#include <gzip/utils.hpp>
#include <gzip/version.hpp>

#include <string>

int main() {
    // All function calls must pass in a pointer of an
    // immutable character sequence (aka a string in C) and its size
    std::string data    = "hello";
    const char* pointer = data.data();
    std::size_t size    = data.size();

    // Check if compressed. Can check both gzip and zlib.
    bool c = gzip::is_compressed(pointer, size);  // false

    // Compress returns a std::string
    std::string compressed_data = gzip::compress(pointer, size);

    // Decompress returns a std::string and decodes both zlib and gzip
    const char* compressed_pointer = compressed_data.data();
    std::string decompressed_data  = gzip::decompress(compressed_pointer, compressed_data.size());

    return 0;
}
