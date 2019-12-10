#include <cstdlib>
#include <iostream>
#include "x265.h"

int main()
{
    x265_param * param = x265_param_alloc();
    x265_param_default(param);
    param->sourceWidth = 640;
    param->sourceHeight = 480;
    param->fpsNum = 25;
    param->fpsDenom = 1;
    x265_encoder * encoder = x265_encoder_open(param);
    x265_encoder_close(encoder);
    x265_param_free(param);
    return EXIT_SUCCESS;
}
