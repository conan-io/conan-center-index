#include <stdio.h>
#include "minmea.h"


int main(void) {
    char* nmea_data = "$GPGGA,155246.585,5231.171,N,01321.830,E,1,12,1.0,0.0,M,0.0,M,,*6F";

    if (minmea_sentence_id(nmea_data, false) == MINMEA_SENTENCE_GGA) {
        struct minmea_sentence_gga frame;
        if (minmea_parse_gga(&frame, nmea_data)) {
            printf("$GGA: fix quality: %d\n", frame.fix_quality);
        }
    }

    return 0;
}
