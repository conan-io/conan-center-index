#include "f2c.h"

extern int cylarea_(real *r__, real *h__, real *v);

#include <stdio.h>

int main() {
    float r, h, a;
    r = 2.f;
    h = 5.f;
    cylarea_(&r, &h, &a);
    printf("Area of cylinder with r=%f, h=%f is %f.\n", r, h, a);
    return 0;
}
