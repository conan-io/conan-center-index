#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <libmodplug/modplug.h>

/* https://github.com/lclevy/unmo3/blob/master/spec/xm.txt */

#pragma pack(push, 1)

typedef struct xm_t
{
    char id_text[17];
    char module_name[20];
    char nl;
    char tracker_name[20];
    uint16_t version;
    uint32_t header_size;
    uint16_t song_length;
    uint16_t restart_position;
    uint16_t number_of_channels;
    uint16_t number_of_patterns;
    uint16_t number_of_instruments;
    uint16_t flags;
    uint16_t default_tempo;
    uint16_t default_bmp;
    uint8_t pattern_order_table[256];
}
xm_t;

#pragma pack(pop)

#define SIZE 0x200

int main(int argc, char * const argv[])
{
    unsigned char b[SIZE];
    FILE * f = NULL;
    long fsize = 0;
    ModPlugFile * m = NULL;
    xm_t * xm = (xm_t*) b;
    memset(b, 0, SIZE);

    memcpy(xm->id_text, "Extended Module:", 17);
    memcpy(xm->module_name,  "My Module           ", 20);
    xm->nl = 0x1A;
    memcpy(xm->tracker_name, "FastTracker II      ", 20);
    xm->version = 0x0103;
    xm->header_size = sizeof(xm_t);
    xm->song_length = 1;
    xm->restart_position = 0;
    xm->number_of_channels = 2;
    xm->number_of_patterns = 0;
    xm->number_of_instruments = 0;
    xm->flags = 1;
    xm->default_tempo = 1;
    xm->default_bmp = 1;

    m = ModPlug_Load(b, SIZE);
    if (!m)
    {
        return -4;
    }
    printf("name: %s\n", ModPlug_GetName(m));
    printf("length: %d ms\n", (int) ModPlug_GetLength(m));

    ModPlug_Unload(m);
    return 0;
}
