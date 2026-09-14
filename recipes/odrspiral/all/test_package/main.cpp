#include <stdio.h>

extern "C" {
#include "odrSpiral.h"
}

int main() {
    double s, t, x, y;

    for ( s = 0.0; s < 300.0; s += 1.0 )
    {
        odrSpiral( s, 0.001, &x, &y, &t );
        fprintf( stderr, "%10.4f %10.4f \n", x, y );
    }

    return 0 ;
}
