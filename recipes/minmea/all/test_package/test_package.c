#include <stdio.h>
#include "minmea.h"

char* nmea_data[] = {
"$GPGGA,155246.585,5231.171,N,01321.830,E,1,12,1.0,0.0,M,0.0,M,,*6F",
"$GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30",
"$GPRMC,155246.585,A,5231.171,N,01321.830,E,5768.0,100.5,120224,000.0,W*44",
"$GPGGA,155247.585,5230.707,N,01324.349,E,1,12,1.0,0.0,M,0.0,M,,*68",
"$GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30",
"$GPRMC,155247.585,A,5230.707,N,01324.349,E,5522.0,077.3,120224,000.0,W*48",
"$GPGGA,155248.585,5231.236,N,01326.712,E,1,12,1.0,0.0,M,0.0,M,,*69",
"$GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30",
"$GPRMC,155248.585,A,5231.236,N,01326.712,E,3306.0,067.4,120224,000.0,W*49",
"$GPGGA,155249.585,5231.753,N,01327.959,E,1,12,1.0,0.0,M,0.0,M,,*6E",
"$GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30",
"$GPRMC,155249.585,A,5231.753,N,01327.959,E,1752.9,291.8,120224,000.0,W*47",
"$GPGGA,155250.585,5232.020,N,01327.289,E,1,12,1.0,0.0,M,0.0,M,,*60",
"$GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30",
"$GPRMC,155250.585,A,5232.020,N,01327.289,E,8124.7,266.3,120224,000.0,W*4A",
"$GPGGA,155251.585,5231.785,N,01323.602,E,1,12,1.0,0.0,M,0.0,M,,*69",
"$GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30",
"$GPRMC,155251.585,A,5231.785,N,01323.602,E,5026.3,260.0,120224,000.0,W*4C",
"$GPGGA,155252.585,5231.399,N,01321.398,E,1,12,1.0,0.0,M,0.0,M,,*67",
"$GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30",
"$GPRMC,155252.585,A,5231.399,N,01321.398,E,3905.6,194.0,120224,000.0,W*41",
"$GPGGA,155253.585,5230.328,N,01321.130,E,1,12,1.0,0.0,M,0.0,M,,*6D",
"$GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30",
"$GPRMC,155253.585,A,5230.328,N,01321.130,E,3905.6,000.0,120224,000.0,W*47",
"$GPGGA,155254.585,5230.328,N,01321.130,E,1,12,1.0,0.0,M,0.0,M,,*6A",
"$GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30",
"$GPRMC,155254.585,A,5230.328,N,01321.130,E,000.0,000.0,120224,000.0,W*79",
};

int main(void) {
    for (int i = 0; i < sizeof(nmea_data) / sizeof(nmea_data[0]); i++) {
        char* line = nmea_data[i];
        switch (minmea_sentence_id(line, false)) {
        case MINMEA_SENTENCE_RMC: {
            struct minmea_sentence_rmc frame;
            if (minmea_parse_rmc(&frame, line)) {
                printf("$RMC: raw coordinates and speed: (%d/%d,%d/%d) %d/%d\n", frame.latitude.value, frame.latitude.scale, frame.longitude.value, frame.longitude.scale, frame.speed.value,
                       frame.speed.scale);
                printf("$RMC fixed-point coordinates and speed scaled to three decimal places: (%d,%d) %d\n", minmea_rescale(&frame.latitude, 1000), minmea_rescale(&frame.longitude, 1000),
                       minmea_rescale(&frame.speed, 1000));
                printf("$RMC floating point degree coordinates and speed: (%f,%f) %f\n", minmea_tocoord(&frame.latitude), minmea_tocoord(&frame.longitude), minmea_tofloat(&frame.speed));
            }
        } break;

        case MINMEA_SENTENCE_GGA: {
            struct minmea_sentence_gga frame;
            if (minmea_parse_gga(&frame, line)) {
                printf("$GGA: fix quality: %d\n", frame.fix_quality);
            }
        } break;

        case MINMEA_SENTENCE_GSV: {
            struct minmea_sentence_gsv frame;
            if (minmea_parse_gsv(&frame, line)) {
                printf("$GSV: message %d of %d\n", frame.msg_nr, frame.total_msgs);
                printf("$GSV: satellites in view: %d\n", frame.total_sats);
                for (int i = 0; i < 4; i++)
                    printf("$GSV: sat nr %d, elevation: %d, azimuth: %d, snr: %d dbm\n", frame.sats[i].nr, frame.sats[i].elevation, frame.sats[i].azimuth, frame.sats[i].snr);
            }
        } break;
        }
    }

    return 0;
}
