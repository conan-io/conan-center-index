#include <DSPark/DSPark.h>

#include <cstdio>

int main()
{
    dspark::AudioSpec spec { 48000.0, 64, 2 };

    dspark::Gain<float> gain;
    gain.prepare(spec);
    gain.setGainDb(-3.0f);

    dspark::Biquad<float, 2> biquad;
    biquad.setCoeffs(dspark::BiquadCoeffs<float>::makeLowPass(48000.0, 1000.0, 0.707));

    float left[64] = {};
    float right[64] = {};
    left[0] = 1.0f;
    right[0] = 1.0f;
    float* channels[2] = { left, right };
    dspark::AudioBufferView<float> view(channels, 2, 64);
    gain.processBlock(view);

    std::printf("DSPark test package: impulse through Gain -> %f\n",
                static_cast<double>(left[0]));
    return 0;
}
