#include "gd.h"

int main() {
    gdImagePtr im;
    im = gdImageCreate(10, 10);
    gdImageDestroy (im);
    return 0;
}
