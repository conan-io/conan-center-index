#include <DSPark.h>

#include <cstdlib>

int main() {
    dspark::Gain<float> gain;
    gain.prepare({48000.0, 64, 2});
    return EXIT_SUCCESS;
}
