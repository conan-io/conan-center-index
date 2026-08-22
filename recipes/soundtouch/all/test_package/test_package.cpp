#include <iostream>

#include "soundtouch/SoundTouch.h"

int main(int argc, char* argv[]) {
    std::cout << "SoundTouch: " << soundtouch::SoundTouch::getVersionString() << "\n";

    soundtouch::SoundTouch soundTouch;
    soundTouch.setRate(0.5);
    soundTouch.setTempo(1.5);
    soundTouch.setPitch(0.8);
    soundTouch.setChannels(2);

    soundTouch.flush();

    return 0;
}
