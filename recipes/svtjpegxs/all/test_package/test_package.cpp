#include <cstdlib>

#include "svt-jpegxs/SvtJpegxs.h"
#include "svt-jpegxs/SvtJpegxsImageBufferTools.h"

int main()
{
    svt_jpeg_xs_frame_pool_free(nullptr);
    return EXIT_SUCCESS;
}
