#include <stddef.h>
#include <stdio.h>
#include <stdlib.h> //for EXIT_FAILURE
#include <locale.h>

#if _MSC_VER && _MSC_VER < 1600
typedef unsigned __int32 uint32_t;
#else
#include <stdint.h>
#endif

#include "iconv.h"
#include "libcharset.h"

int main()
{
    // Test libiconv
    char in_bytes[4] = {'c', 'i', 'a', 'o'};
    char *in_buffer = (char *)&in_bytes;
    size_t in_bytes_left = sizeof(char) * 4;
    uint32_t ou_bytes[4] = {(uint32_t)-1, (uint32_t)-1, (uint32_t)-1, (uint32_t)-1};
    size_t ou_bytes_left = sizeof(uint32_t) * 4;
    char *ou_buffer = (char *)&ou_bytes;
    iconv_t context;
    size_t rv;

    context = iconv_open("UCS-4-INTERNAL", "US-ASCII");
    if ((iconv_t)(-1) == context)
    {
        fprintf(stderr, "iconv_open failed\n");
        return EXIT_FAILURE;
    }

    rv = iconv(context, &in_buffer, &in_bytes_left, &ou_buffer, &ou_bytes_left);
    if ((size_t)(-1) == rv)
    {
        fprintf(stderr, "icon failed\n");
        return EXIT_FAILURE;
    }

    printf("retval libiconv: %lu %u %u %u %u\n", rv, ou_bytes[0], ou_bytes[1], ou_bytes[2], ou_bytes[3]);

    iconv_close(context);

    // Test libcharset
    setlocale(LC_ALL, "");
    printf("retval libcharset: %s\n", locale_charset());

    return EXIT_SUCCESS;
}
