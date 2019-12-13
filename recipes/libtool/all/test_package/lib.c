#include <math.h>
#include <stdio.h>

double my_function(double val) {
    fprintf(stderr, "inside my_function(%e)\n", val);
    return sin(val);
}
