#include "alc.h"
#include "al.h"
#include "alext.h"

#include <stdio.h>
#include <string.h>

static ALenum checkALErrors(int linenum)
{
    ALenum err = alGetError();
    if(err != AL_NO_ERROR)
        printf("OpenAL Error: %s (0x%x), @ %d\n", alGetString(err), err, linenum);
    return err;
}
#define checkALErrors() checkALErrors(__LINE__)

static ALCenum checkALCErrors(ALCdevice *device, int linenum)
{
    ALCenum err = alcGetError(device);
    if(err != ALC_NO_ERROR)
        printf("ALC Error: %s (0x%x), @ %d\n", alcGetString(device, err), err, linenum);
    return err;
}
#define checkALCErrors(x) checkALCErrors((x),__LINE__)

#define MAX_WIDTH  80

static void printList(const char *list, char separator)
{
    size_t col = MAX_WIDTH, len;
    const char *indent = "    ";
    const char *next;

    if(!list || *list == '\0')
    {
        fprintf(stdout, "\n%s!!! none !!!\n", indent);
        return;
    }

    do {
        next = strchr(list, separator);
        if(next)
        {
            len = next-list;
            do {
                next++;
            } while(*next == separator);
        }
        else
            len = strlen(list);

        if(len + col + 2 >= MAX_WIDTH)
        {
            fprintf(stdout, "\n%s", indent);
            col = strlen(indent);
        }
        else
        {
            fputc(' ', stdout);
            col++;
        }

        len = fwrite(list, 1, len, stdout);
        col += len;

        if(!next || *next == '\0')
            break;
        fputc(',', stdout);
        col++;

        list = next;
    } while(1);
    fputc('\n', stdout);
}

static void printALCInfo(ALCdevice *device)
{
    ALCint major, minor;

    if(device)
    {
        const ALCchar *devname = NULL;
        printf("\n");
        if(alcIsExtensionPresent(device, "ALC_ENUMERATE_ALL_EXT") != AL_FALSE)
            devname = alcGetString(device, ALC_ALL_DEVICES_SPECIFIER);
        if(checkALCErrors(device) != ALC_NO_ERROR || !devname)
            devname = alcGetString(device, ALC_DEVICE_SPECIFIER);
        printf("** Info for device \"%s\" **\n", devname);
    }
    alcGetIntegerv(device, ALC_MAJOR_VERSION, 1, &major);
    alcGetIntegerv(device, ALC_MINOR_VERSION, 1, &minor);
    if(checkALCErrors(device) == ALC_NO_ERROR)
        printf("ALC version: %d.%d\n", major, minor);
    if(device)
    {
        printf("ALC extensions:");
        printList(alcGetString(device, ALC_EXTENSIONS), ' ');
        checkALCErrors(device);
    }
}

static void printDeviceList(const char *list)
{
    if(!list || *list == '\0')
        printf("    !!! none !!!\n");
    else do {
        printf("    %s\n", list);
        list += strlen(list) + 1;
    } while(*list != '\0');
}

int main(int argc, char **argv)
{
    printf("Available playback devices:\n");
    if(alcIsExtensionPresent(NULL, "ALC_ENUMERATE_ALL_EXT") != AL_FALSE)
        printDeviceList(alcGetString(NULL, ALC_ALL_DEVICES_SPECIFIER));
    else
        printDeviceList(alcGetString(NULL, ALC_DEVICE_SPECIFIER));
    printf("Available capture devices:\n");
    printDeviceList(alcGetString(NULL, ALC_CAPTURE_DEVICE_SPECIFIER));

    if(alcIsExtensionPresent(NULL, "ALC_ENUMERATE_ALL_EXT") != AL_FALSE)
        printf("Default playback device: %s\n",
               alcGetString(NULL, ALC_DEFAULT_ALL_DEVICES_SPECIFIER));
    else
        printf("Default playback device: %s\n",
               alcGetString(NULL, ALC_DEFAULT_DEVICE_SPECIFIER));
    printf("Default capture device: %s\n",
           alcGetString(NULL, ALC_CAPTURE_DEFAULT_DEVICE_SPECIFIER));

    printALCInfo(NULL);

    return 0;
}
