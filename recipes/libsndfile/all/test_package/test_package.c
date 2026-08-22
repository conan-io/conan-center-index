#include "sndfile.h"

#include <stdio.h>

int main(int argc, char *argv[]) {
	if (argc < 2) {
		puts("Usage: example <file.wav>\n");
		return 0;
	}
	SF_INFO sfinfo;
    SNDFILE *infile = sf_open (argv[1], SFM_READ, &sfinfo);
    printf("Sample rate: %d\n", sfinfo.samplerate);
	return 0;
}
