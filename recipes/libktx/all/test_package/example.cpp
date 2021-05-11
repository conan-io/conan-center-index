#include <ktx.h>

#include <iostream>

int main(int argc, char **argv)
{
    if (argc < 2) {
        std::cerr << "Need at least one argument\n";
        return 1;
    }
    ktxTexture* texture;
    KTX_error_code result;
    result = ktxTexture_CreateFromNamedFile("mytex3d.ktx",
                                            KTX_TEXTURE_CREATE_LOAD_IMAGE_DATA_BIT,
                                            &texture);


    return 0;
}
