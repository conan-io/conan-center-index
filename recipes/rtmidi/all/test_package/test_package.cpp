#include <iostream>

#include <RtMidi.h>

int main (void) {
    std::cout << "Version: " << RtMidi::getVersion() << std::endl;

    return 0;
}
