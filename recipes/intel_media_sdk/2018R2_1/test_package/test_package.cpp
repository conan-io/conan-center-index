#include <cstdlib>
#include <iostream>
#include <mfx/mfxsession.h>

int main()
{
    mfxSession session;
    mfxVersion v;
    mfxStatus status = MFXInit(MFX_IMPL_SOFTWARE, NULL, &session);
    if (status != MFX_ERR_NONE) {
        std::cerr << "MFXInit failed with error " << status << std::endl;
        return EXIT_SUCCESS;
    }
    status = MFXQueryVersion(session, &v);
    if (status != MFX_ERR_NONE) {
        std::cerr << "MFXQueryVersion failed with error " << status << std::endl;
        MFXClose(session);
        return EXIT_SUCCESS;
    }
    std::cout << "MFX version " << v.Version << std::endl;
    MFXClose(session);
    return EXIT_SUCCESS;
}
