#include <stdio.h>
#include <string.h>

#include "slz.h"

int main(void) {
	struct slz_stream strm;
	slz_make_crc_table();
	slz_prepare_dist_table();

  slz_init(&strm, 3, SLZ_FMT_GZIP);

  return 0;
}
