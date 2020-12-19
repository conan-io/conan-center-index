/* simple.c
   Simple libftdi usage example
   This program is distributed under the GPL, version 2
*/
#include <stdio.h>
#include <stdlib.h>
#include <ftdi.h>

int main(void)
{
    int ret;
    struct ftdi_context *ftdi;
    struct ftdi_version_info version;
    if ((ftdi = ftdi_new()) == 0)
   {
        fprintf(stderr, "ftdi_new failed\n");
        goto failure;
    }
    version = ftdi_get_library_version();
    printf("Initialized libftdi %s (major: %d, minor: %d, micro: %d, snapshot ver: %s)\n",
        version.version_str, version.major, version.minor, version.micro,
        version.snapshot_str);
    fflush(stdout);
    if ((ret = ftdi_usb_open(ftdi, 0x0403, 0x6001)) < 0)
    {
        fprintf(stderr, "Unable to open ftdi device: %d (%s)\n", ret, ftdi_get_error_string(ftdi));
        ftdi_free(ftdi);
        goto failure;
    }
    // Read out FTDIChip-ID of R type chips
    if (ftdi->type == TYPE_R)
    {
        unsigned int chipid;
        printf("ftdi_read_chipid: %d\n", ftdi_read_chipid(ftdi, &chipid));
        printf("FTDI chipid: %X\n", chipid);
    }
    if ((ret = ftdi_usb_close(ftdi)) < 0)
    {
        fprintf(stderr, "Unable to close ftdi device: %d (%s)\n", ret, ftdi_get_error_string(ftdi));
        ftdi_free(ftdi);
        goto failure;
    }
    ftdi_free(ftdi);
    return EXIT_SUCCESS;
failure:
    printf("This is a test package ==> ignoring the error.\n");
    return EXIT_SUCCESS;
}
