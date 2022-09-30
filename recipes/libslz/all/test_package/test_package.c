#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "slz.h"

int main(void) {
	struct slz_stream strm;
	unsigned char *outbuf;

	slz_make_crc_table();
	slz_prepare_dist_table();

	slz_init(&strm, 3, SLZ_FMT_GZIP);

	outbuf = calloc(1, 1024 * 1024 * 2 + 4096);

	slz_finish(&strm, outbuf);

	return 0;
}
