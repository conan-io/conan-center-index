#include <rtmidi/RtMidi.h>

int main (void) {
    try {
        RtMidiIn midiIn(RtMidi::RTMIDI_DUMMY);
    } catch ( RtMidiError &error ) {
        error.printMessage();
    }

    return 0;
}
