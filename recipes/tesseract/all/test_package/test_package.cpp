#include <stdio.h>
#include <leptonica/allheaders.h>
#include <tesseract/baseapi.h>

int main(int argc, char **argv) {
	printf("Tesseract version: %s\n", tesseract::TessBaseAPI::Version());
	printf("Leptonica version: %d.%d.%d\n", LIBLEPT_MAJOR_VERSION, LIBLEPT_MINOR_VERSION, LIBLEPT_PATCH_VERSION);
	printf("Lib versions: %s\n", getImagelibVersions());
	return 0;
}

