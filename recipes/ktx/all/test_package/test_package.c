#include <ktx.h>

#include <stdio.h>

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "Need at least one argument\n");
        return 1;
    }

    ktxTexture* texture;
    KTX_error_code result;
    result = ktxTexture_CreateFromNamedFile(argv[1],
                                            KTX_TEXTURE_CREATE_LOAD_IMAGE_DATA_BIT,
                                            &texture);

    return 0;
}
