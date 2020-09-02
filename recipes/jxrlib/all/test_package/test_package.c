#include <stdio.h>

#include <JXRTest.h>

int main(int argc, char* argv[])
{
    if (argc < 2) {
        fprintf(stderr, "Need at least one argument\n");
        return 1;
    }

    const char *jxr_path = argv[1];

    {
        ERR err = WMP_errSuccess;

        PKCodecFactory* pCodecFactory = NULL;
        PKImageDecode* pDecoder = NULL;

        Call(PKCreateCodecFactory(&pCodecFactory, WMP_SDK_VERSION));
        Call(pCodecFactory->CreateDecoderFromFile(jxr_path, &pDecoder));

        PKPixelFormatGUID pix_frmt;
        Call(pDecoder->GetPixelFormat(pDecoder, &pix_frmt));

    Cleanup:
        if(pDecoder) pDecoder->Release(&pDecoder);
        if(pCodecFactory) pCodecFactory->Release(&pCodecFactory);
    }

    return 0;
}
