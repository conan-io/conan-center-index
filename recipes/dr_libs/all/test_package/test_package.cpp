#define DR_WAV_IMPLEMENTATION
#include "dr_wav.h"
#include <vector>
#include <iostream>

int main() {
    // Read in from a file
    drwav wav;
    if (!drwav_init_file(&wav, "sample.wav", nullptr)) {
        std::cout << "Failed to read in the wav file!" << std::endl;
        return DRWAV_INVALID_FILE;
    }

    // Read in the PCM data
    std::vector<drwav_int16> buffer(wav.totalPCMFrameCount * wav.channels);
    auto samplesDecoded = drwav_read_pcm_frames_s16__pcm(&wav, buffer.size(), buffer.data());
    if (samplesDecoded != buffer.size() / wav.channels) {
        std::cout << "Didn't decode the whole file! Wav file had " << wav.totalPCMFrameCount << " frames, but only "
            <<samplesDecoded << "were decoded." << std::endl;
        return DRWAV_ERROR;
    }

    // Close the file
    auto result = drwav_uninit(&wav);
    if (result != DRWAV_SUCCESS) {
        std::cout << "Failed to uninit the wav file!" << std::endl;
        return result;
    }

    // Convert it to 32-bit floating point
    std::vector<float> asFloat(samplesDecoded);
    drwav_s16_to_f32(asFloat.data(), buffer.data(), samplesDecoded);

    // If we get here with no issues, then it's a success
    std::cout << "Test success!" << std::endl;
    return DRWAV_SUCCESS;
}