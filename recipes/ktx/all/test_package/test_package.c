#include <ktx.h>

#include <stdio.h>

int main(int argc, char **argv)
{
    ktxTexture* texture;
    KTX_error_code result;
    result = ktxTexture_CreateFromNamedFile("fake-file.ktx",
                                            KTX_TEXTURE_CREATE_LOAD_IMAGE_DATA_BIT,
                                            &texture);

    printf("Test: %s\n", ktxErrorString(result));
    return 0;
}
