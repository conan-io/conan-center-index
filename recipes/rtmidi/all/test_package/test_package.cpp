#include <rtmidi/RtMidi.h>

int main (void) {
    try {
        RtMidiIn *midiIn = new RtMidiIn();
        delete midiIn;
    } catch ( RtMidiError &error ) {
        error.printMessage();
    }
}
