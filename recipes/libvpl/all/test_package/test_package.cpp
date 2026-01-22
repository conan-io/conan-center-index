#include <vpl/mfx.h>

#include <iostream>
#include <cstdlib>

int main() {
    mfxLoader loader = MFXLoad();
    if (!loader) {
        return 1;
    }

    mfxSession session{};
    mfxStatus sts = MFXCreateSession(loader, 0, &session);
    if (sts == MFX_ERR_NONE) {
        MFXClose(session);
        MFXUnload(loader);
        std::cout << "Linking OK, VPL runtime available on system" << std::endl;
        return 0;
    }

    MFXUnload(loader);
    std::cout << "Linking OK, VPL runtime unavailable on system" << std::endl;
    return 0;
}
