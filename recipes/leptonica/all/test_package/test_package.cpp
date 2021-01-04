#include <stdio.h>
#include <leptonica/allheaders.h>

int main(int argc, char **argv) {
	printf("Leptonica version: %d.%d.%d\n", LIBLEPT_MAJOR_VERSION, LIBLEPT_MINOR_VERSION, LIBLEPT_PATCH_VERSION);
	printf("Lib versions: %s\n", getImagelibVersions());
	return 0;
}
