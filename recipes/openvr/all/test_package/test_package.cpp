#include <openvr.h>

#include <cstdlib>

int main()
{
    vr::EVRInitError eError = vr::VRInitError_None;
    vr::IVRSystem *pHMD = vr::VR_Init( &eError, vr::VRApplication_Scene );
    vr::VR_Shutdown();
    return EXIT_SUCCESS;
}
