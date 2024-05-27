#include <stdio.h>

#include <JXRTest.h>

int main(int argc, char* argv[])
{
    PKCodecFactory* pCodecFactory = NULL;

    Call(PKCreateCodecFactory(&pCodecFactory, WMP_SDK_VERSION));
    
    if(pCodecFactory) {
        pCodecFactory->Release(&pCodecFactory)
    }

    return 0;
}
