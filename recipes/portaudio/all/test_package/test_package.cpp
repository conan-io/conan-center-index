#include <portaudio.h>
#include <iostream>

int main() {
    PaError err = Pa_Initialize();
    if (err != paNoError) {
        std::cerr << "PortAudio init error: " << Pa_GetErrorText(err) << "\n";
        return 1;
    }

    std::cout << "PortAudio version: " << Pa_GetVersionText() << "\n";

    int deviceCount = Pa_GetDeviceCount();
    if (deviceCount < 0) {
        std::cerr << "ERROR: Pa_GetDeviceCount returned " << deviceCount << "\n";
        return 1;
    }

    for (int i = 0; i < deviceCount; ++i) {
        const PaDeviceInfo* deviceInfo = Pa_GetDeviceInfo(i);
        const PaHostApiInfo* hostApiInfo = Pa_GetHostApiInfo(deviceInfo->hostApi);
        std::cout << "Device #" << i << ": " << deviceInfo->name
                  << " [API: " << hostApiInfo->name << "]\n";
    }

    Pa_Terminate();
    return 0;
}
