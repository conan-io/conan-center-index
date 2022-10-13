#include "lzo1f.h"
#include <stdio.h>
#include <string.h>

const char *text = "This is a string that lzo should compress to less bytes then before if it is working fine.\n"
"This compression algorithm appears to only compress bigger inputs so put a lot of text here.\n";


int main()
{
    if (lzo_init() != LZO_E_OK)
    {
        printf("internal error - lzo_init() failed !!!\n");
        printf("(this usually indicates a compiler bug - try recompiling\nwithout optimizations, and enable '-DLZO_DEBUG' for diagnostics)\n");
        return 1;
    }

    char compressed[2048];
    size_t compressed_len = sizeof(compressed);
    {
        char workMemory[LZO1F_MEM_COMPRESS+1];
        int r = lzo1f_1_compress((unsigned char*)text, strlen(text), (unsigned char*)compressed, &compressed_len, workMemory);
        if (r != LZO_E_OK) {
            printf("internal error - compression failed: %d\n", r);
            return 1;
        }
    }
    printf("Size before compression: %zu bytes\n", strlen(text));
    printf("Size after compression:  %zu bytes\n", compressed_len);


    char decompressed[2048];
    size_t decompressed_len = sizeof(decompressed);
    {
        char workMemory[LZO1F_MEM_DECOMPRESS+1];
        int r = lzo1f_decompress((unsigned char*)compressed, compressed_len, (unsigned char*)decompressed, &decompressed_len, workMemory);
        if (r != LZO_E_OK) {
            printf("internal error - decompression failed: %d\n", r);
            return 1;
        }
    }

    int ok = (strlen(text) == decompressed_len) && (strncmp(text, decompressed, decompressed_len) == 0);
    printf("Decompression: %s\n", ok ? "Success" : "Failure");

    return ok ? 0 : 1;
}
