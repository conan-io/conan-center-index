#include <cstdlib>
#include <iostream>
#include "gmtl/gmtl.h"


int main(void) {
    
	gmtl::Vec4f     homogeneousVec;
    gmtl::Vec4f     homogeneousVec2;
    gmtl::Matrix44f mat;
 
    homogeneousVec2 = mat * homogeneousVec;

    gmtl::xform(homogeneousVec2, mat, homogeneousVec);
    return EXIT_SUCCESS;
}
