/* simple.c

   Simple libftdi usage example

   This program is distributed under the GPL, version 2
*/

#include <stdio.h>
#include <ftdi.h>

int main(void)
{
    int ret;
    struct ftdi_context ftdic;
    if (ftdi_init(&ftdic) < 0)
    {
        fprintf(stderr, "ftdi_init failed\n");
        return EXIT_FAILURE;
    }

    if ((ret = ftdi_usb_open(&ftdic, 0x0403, 0x6001)) < 0)
    {
        fprintf(stderr, "unable to open ftdi device: %d (%s)\n", ret, ftdi_get_error_string(&ftdic));
        goto failure;
    }

    // Read out FTDIChip-ID of R type chips
    if (ftdic.type == TYPE_R)
    {
        unsigned int chipid;
        printf("ftdi_read_chipid: %d\n", ftdi_read_chipid(&ftdic, &chipid));
        printf("FTDI chipid: %X\n", chipid);
    }

    if ((ret = ftdi_usb_close(&ftdic)) < 0)
    {
        fprintf(stderr, "unable to close ftdi device: %d (%s)\n", ret, ftdi_get_error_string(&ftdic));
        goto failure;
    }

    ftdi_deinit(&ftdic);

    return EXIT_SUCCESS;
failure:
    printf("This is a test package ==> ignoring the error.\n");
    return EXIT_SUCCESS;
}
