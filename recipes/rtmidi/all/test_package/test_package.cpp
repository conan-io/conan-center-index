#include <rtmidi/RtMidi.h>

int main (void) {
    try {
        RtMidiOut *midiout = new RtMidiOut();
    } catch ( RtMidiError &error ) {
        error.printMessage();
    }
}
