#include "PxConfig.h"
#include "PxPhysicsAPI.h"

using namespace physx;

#if defined(_WINDOWS)
#include <windows.h>

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID    lpvReserved) {
    return TRUE;
}

#define EXPORTS __declspec(dllexport)
#else
#define EXPORTS
#endif

PxDefaultAllocator gAllocator;
PxDefaultErrorCallback gErrorCallback;

EXPORTS
void some_func(void) {
    PxFoundation *gFoundation = PxCreateFoundation(PX_PHYSICS_VERSION, gAllocator, gErrorCallback);
    gFoundation->release();
}
