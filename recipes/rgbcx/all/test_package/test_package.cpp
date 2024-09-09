// Workaround for a missing math.h include in rgbcx.h
#include <cmath>

#define RGBCX_IMPLEMENTATION
#include "rgbcx.h"

int main()
{
    rgbcx::init(rgbcx::bc1_approx_mode::cBC1Ideal);
    return 0;
}
