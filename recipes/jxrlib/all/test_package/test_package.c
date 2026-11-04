#include <stdio.h>

#include <JXRTest.h>

int main(int argc, char* argv[])
{
    ERR err = WMP_errSuccess;
    PKCodecFactory* pCodecFactory = NULL;

    Call(PKCreateCodecFactory(&pCodecFactory, WMP_SDK_VERSION));

    Cleanup:
    if(pCodecFactory) {
        pCodecFactory->Release(&pCodecFactory);
    }

    return 0;
}
