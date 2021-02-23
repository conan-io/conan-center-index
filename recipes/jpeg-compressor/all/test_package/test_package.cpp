#include <iostream>

#include "jpge.h"
#include "jpgd.h"

int main(int argc, const char* argv[])
{
    if (argc < 2) {
        std::cerr << "Need at least one argument" << std::endl;
        return 1;
    }

    const char* pSrc_filename = argv[1];

    const int req_comps = 4;
    int width = 0, height = 0, actual_comps = 0;
    uint8_t* pImage_data = jpgd::decompress_jpeg_image_from_file(pSrc_filename, &width, &height, &actual_comps, req_comps);
    if (!pImage_data)
    {
        std::cerr << "Failed loading file " << pSrc_filename << std::endl;
        return EXIT_FAILURE;
    }

    int buf_size = width * height * 3;
    if (buf_size < 1024) buf_size = 1024;
    void* pBuf = malloc(buf_size);
    if (!jpge::compress_image_to_jpeg_file_in_memory(pBuf, buf_size, width, height, req_comps, pImage_data))
    {
        std::cerr << "Failed creating JPEG data" << std::endl;
        return EXIT_FAILURE;
    }

    free(pBuf);
    free(pImage_data);

    return EXIT_SUCCESS;
}
