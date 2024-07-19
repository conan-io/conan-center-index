#include <stdio.h>
#include <stdlib.h>

#include "jxl/decode.h"
#include "jxl/thread_parallel_runner.h"

int main()
{
    JxlDecoder *dec = NULL;
    void *runner = NULL;
    dec = JxlDecoderCreate(NULL);

    // Allways True
    if (JxlDecoderSubscribeEvents(dec, JXL_DEC_BASIC_INFO) == JXL_DEC_SUCCESS)
    {
        printf("Test");
    }
}
