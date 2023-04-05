#include "testlib_private.h"

#include <math.h>
#include <stdio.h>

double my_function(double val) {
    fprintf(stderr, "inside my_function(%e)\n", val);
    return sqrt(val);
}

TESTLIB_API const int libtestlib_value = 42;
