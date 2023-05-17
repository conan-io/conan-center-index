#include "lcms2.h"

int main()
{
    cmsUInt16Number linear[2] = { 0, 0xffff };
    cmsToneCurve * curve = cmsBuildTabulatedToneCurve16(0, 2, linear);
    cmsFreeToneCurve(curve);
}
