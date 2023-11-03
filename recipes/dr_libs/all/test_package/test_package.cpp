#define DR_WAV_IMPLEMENTATION
#include "dr_wav.h"
#include <vector>
#include <iostream>
#include <random>

#define BUFFER_SIZE 255

int main() {
    srand(time(NULL));

    // Create fake PCM data
    std::vector<drwav_int16> buffer(BUFFER_SIZE);
    for (size_t i = 0; i < BUFFER_SIZE; i++)
        buffer[i] = rand() % std::numeric_limits<drwav_int16>::max();

    // Convert it to 32-bit floating point
    std::vector<float> asFloat(buffer.size());
    drwav_s16_to_f32(asFloat.data(), buffer.data(), buffer.size());

    // If we get here with no issues, then it's a success
    std::cout << "Test success!" << std::endl;
    return DRWAV_SUCCESS;
}
