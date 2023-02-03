#include <iostream>

#include "PerlinNoise.hpp"

int main(int argc, const char** argv) {
    auto frequency = 32.f;
    auto octaves = 9;
    auto seed = siv::PerlinNoise::seed_type{74524};

    auto generator = siv::PerlinNoise{seed};

    auto width = 32;
    auto height = 16;

    auto fx = width / frequency;
    auto fy = height / frequency;

    for (auto y = 0; y < height; ++y) {
        for (auto x = 0; x < width; ++x) {
            auto color = generator.octave2D(x / fx, y / fy, octaves);
            std::cout << color << " ";
        }
        std::cout << std::endl;
    }

    return 0;
}
