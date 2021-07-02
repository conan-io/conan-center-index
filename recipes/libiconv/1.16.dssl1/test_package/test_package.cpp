#include <cstddef>
#include <iostream>
#include <iconv.h>
#include <cstdlib> //for EXIT_FAILURE

#if _MSC_VER && _MSC_VER<1600
typedef unsigned __int32 uint32_t;
#else
#include <cstdint>
#endif

int main() {
    iconv_t context = iconv_open("UCS-4-INTERNAL", "US-ASCII");
    if ((iconv_t)(-1) == context) {
        std::cerr << "iconv_open failed" << std::endl;
        return EXIT_FAILURE;
    }
    char in_bytes[4] = {'c', 'i', 'a', 'o'};
    char *in_buffer = (char*)&in_bytes;
    size_t in_bytes_left = sizeof(char) * 4;
    uint32_t ou_bytes[4] = { (uint32_t)-1, (uint32_t)-1, (uint32_t)-1, (uint32_t)-1 };
    size_t ou_bytes_left = sizeof(uint32_t) * 4;
    char *ou_buffer = (char*)&ou_bytes;
    size_t rv = iconv(context, &in_buffer, &in_bytes_left, &ou_buffer, &ou_bytes_left);
    if ((size_t)(-1) == rv) {
        std::cerr << "icon failed" << std::endl;
        return EXIT_FAILURE;
    }
    std::cout << "retval " << rv;
    std::cout << " " << (unsigned long)ou_bytes[0];
    std::cout << " " << (unsigned long)ou_bytes[1];
    std::cout << " " << (unsigned long)ou_bytes[2];
    std::cout << " " << (unsigned long)ou_bytes[3];
    std::cout << std::endl;

    iconv_close(context);
}
