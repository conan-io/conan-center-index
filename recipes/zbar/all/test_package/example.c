#include <stdio.h>
#include <zbar.h>

zbar_image_scanner_t *scanner = NULL;

int main (int argc, char **argv)
{

    /* create a reader */
    scanner = zbar_image_scanner_create();

    /* configure the reader */
    zbar_image_scanner_set_config(scanner, 0, ZBAR_CFG_ENABLE, 1);


    /* clean up */
    zbar_image_scanner_destroy(scanner);

	unsigned VersionMajor;
	unsigned VersionMinor;
	unsigned VersionPatch;
	zbar_version(&VersionMajor, &VersionMinor, &VersionPatch);

	printf("Compiled ZBar version %d.%d.%d \n", VersionMajor, VersionMinor, VersionPatch);

	printf("ZBar Test Completed \n");

    return(0);
}
