#include <iostream>
#include "portmidi.h"
#include "porttime.h"

int main() {
    PmStream * midi;
    char line[80];
    int32_t off_time;
    int chord[] = { 60, 67, 76, 83, 90 };
    #define chord_size 5
    PmEvent buffer[chord_size];
    PmTimestamp timestamp;
}
