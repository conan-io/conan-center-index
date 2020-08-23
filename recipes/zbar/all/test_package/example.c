#include <stdio.h>
#include <stdlib.h>
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
	zbar_version(&VersionMajor, &VersionMinor);

	printf("Compiled ZBar version %d.%d \n", VersionMajor, VersionMinor);

	printf("Zbar Test Completed \n");

    return(0);
}
