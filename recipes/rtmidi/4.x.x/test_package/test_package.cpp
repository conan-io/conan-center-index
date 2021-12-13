#include <RtMidi.h>

int main (void) {
    try {
        RtMidiOut *midiout = new RtMidiOut();
        delete midiout;
    } catch ( RtMidiError &error ) {
        error.printMessage();
    }
}
