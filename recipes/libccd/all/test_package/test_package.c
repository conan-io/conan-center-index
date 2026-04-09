#include <ccd/ccd.h>
#include <ccd/vec3.h>

// Force the same condition as MuJoCo: building a DLL that uses ccd
__declspec(dllexport) void test(void) {
    ccd_vec3_t dir;
    ccdVec3Set(&dir, 0.0, 0.0, 0.0);
    if (ccdVec3Eq(&dir, ccd_vec3_origin)) {}
}