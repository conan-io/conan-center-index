#include <brunsli/jpeg_data.h>
#include <brunsli/types.h>
#include <brunsli/jpeg_data_reader.h>

int main() {
    brunsli::JPEGData jpg;
    const size_t input_size = 100;
    const uint8_t input_data[input_size] = {};
    bool ok = brunsli::ReadJpeg(input_data, input_size, brunsli::JPEG_READ_ALL, &jpg);
}
