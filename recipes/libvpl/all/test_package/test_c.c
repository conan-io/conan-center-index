#include <vpl/mfxdispatcher.h>

int main(void)
{
    mfxLoader loader = MFXLoad();
    if (!loader)
        return 1;
    MFXUnload(loader);
    return 0;
}
