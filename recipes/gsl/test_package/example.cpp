#include <iostream>
#include <gsl/gsl_sf_bessel.h>


/**
 * The example program from the GSL documentation
 * http://www.gnu.org/software/gsl/doc/html/usage.html#an-example-program
 */


int main (void) {
    double x = 5.0;
    double y = gsl_sf_bessel_J0 (x);
    printf ("J0(%g) = %.18e\n", x, y);
    return 0;
}

