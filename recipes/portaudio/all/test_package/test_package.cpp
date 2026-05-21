#include <portaudio.h>
#include <iostream>

int main() {
    std::cout << "PortAudio version: " << Pa_GetVersionText() << "\n";
    return 0;
}
