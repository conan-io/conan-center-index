#include <CCfits/CCfits>

int main() {
    long naxis = 2;
    long naxes[2] = {10, 20};
    CCfits::FITS fits("test.fit", USHORT_IMG, naxis, naxes);
    return 0;
}
