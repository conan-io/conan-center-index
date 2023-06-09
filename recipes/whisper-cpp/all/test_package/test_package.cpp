#include <iostream>
#include <memory>
#include <vector>
#include "whisper.h"
#include "dr_wav.h"


int main(void) {
    // Read in from a file
    drwav wav;
    if (!drwav_init_file(&wav, "sample.wav", nullptr)) {
        std::cout << "Failed to read in the wav file!" << std::endl;
        return DRWAV_INVALID_FILE;
    }

    // Read in the PCM data
    std::vector<drwav_int16> buffer(wav.totalPCMFrameCount * wav.channels);
    auto samplesDecoded = drwav_read_pcm_frames_s16(&wav, buffer.size(), buffer.data());
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

    std::string model; // TODO: Get the model

    // Don't worry about manual memory management
    auto context = std::unique_ptr<whisper_context, void(*)(whisper_context*)>(
            whisper_init_from_file(model.data()), whisper_free);

    // TODO: Transcribe the JFK quote and verify that it's correct based on the model

    return EXIT_SUCCESS;
}