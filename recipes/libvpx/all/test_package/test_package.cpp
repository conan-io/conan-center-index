#include <vpx/vpx_codec.h>

#include <cstdlib>
#include <iostream>

int main()
{
    std::cout << "vpx version " << vpx_codec_version_str() << std::endl;
    return EXIT_SUCCESS;
}
