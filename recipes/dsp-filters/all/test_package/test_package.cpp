#include <DspFilters/Dsp.h>

#include <stdio.h>

int main() {
    Dsp::SimpleFilter<Dsp::Butterworth::HighPass<1>, 1> f;
    f.setup(1, 100, 1000);
    f.reset();

    return 0;
}
