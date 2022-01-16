#include <rtmidi/RtMidi.h>

int main (void) {
    try {
        RtMidiIn *midiIn = new RtMidiIn(RtMidi::RTMIDI_DUMMY);
        delete midiIn;
    } catch ( RtMidiError &error ) {
        error.printMessage();
    }

    return 0;
}
