#include <vpl/mfx.h>
#include <iostream>
#include <cstdlib>

int main() {
    // Initialize VPL loader
    mfxLoader loader = MFXLoad();
    if (!loader) {
        std::cout << "Failed to create VPL loader" << std::endl;
        return EXIT_FAILURE;
    }

    // Create a session
    mfxSession session = nullptr;
    mfxStatus sts = MFXCreateSession(loader, 0, &session);
    if (sts != MFX_ERR_NONE) {
        std::cout << "Failed to create session. Status: " << sts << std::endl;
        MFXUnload(loader);
        return EXIT_FAILURE;
    }

    // Print the VPL API version
    mfxVersion version = { {0, 1} };
    mfxStatus status = MFXQueryVersion(session, &version);

    if (status == MFX_ERR_NONE) {
        std::cout << "VPL API version: " << version.Major << "." << version.Minor << std::endl;
    } else {
        std::cout << "Failed to query VPL API version. Status: " << status << std::endl;
    }

    // Clean up
    MFXClose(session);
    MFXUnload(loader);

    return EXIT_SUCCESS;
}
