#include <rawmidi.h>

int main()
{
    rawmidi_hw_print_info("/dev/midi");
    return 0;
}
