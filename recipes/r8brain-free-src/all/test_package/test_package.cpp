#include "r8bbase.h"
#include "CDSPResampler.h"

int main() {
    r8b::CDSPResampler24 resampler(44100.0f, 48000.0f, 512);
}
