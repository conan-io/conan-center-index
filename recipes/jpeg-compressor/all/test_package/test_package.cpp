#include <iostream>

#include "jpge.h"
#include "jpgd.h"

int main(int argc, const char* argv[])
{
    const char* pSrc_filename = "non-real-file.jpg";

    const int req_comps = 4;
    int width = 0, height = 0, actual_comps = 0;
    uint8_t* pImage_data = jpgd::decompress_jpeg_image_from_file(pSrc_filename, &width, &height, &actual_comps, req_comps);
    if (!pImage_data)
    {
        std::cerr << "Test jpgd function" << std::endl;// Always displayed
    }

    int buf_size = width * height * 3;
    void* pBuf = malloc(buf_size);
    if (!jpge::compress_image_to_jpeg_file_in_memory(pBuf, buf_size, width, height, req_comps, pImage_data))
    {
        std::cerr << "Test jpge function" << std::endl;// Always displayed
    }

    free(pBuf);
    free(pImage_data);

    return EXIT_SUCCESS;
}
