#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#include "streamvbyte.h"

#ifdef __clang__
#pragma clang diagnostic ignored "-Wdeclaration-after-statement"
#pragma clang diagnostic ignored "-Wunused-variable"
#endif

int main(void) {
	uint32_t N = 5000U;
	uint32_t * datain = malloc(N * sizeof(uint32_t));
	uint8_t * compressedbuffer = malloc(streamvbyte_max_compressedbytes(N));
	uint32_t * recovdata = malloc(N * sizeof(uint32_t));
	for (uint32_t k = 0; k < N; ++k)
		datain[k] = 120;
	size_t compsize = streamvbyte_encode(datain, N, compressedbuffer); // encoding
	// here the result is stored in compressedbuffer using compsize bytes
	size_t compsize2 = streamvbyte_decode(compressedbuffer, recovdata,
					N); // decoding (fast)
	assert(compsize == compsize2);
	free(datain);
	free(compressedbuffer);
	free(recovdata);
	printf("Compressed %d integers down to %d bytes.\n",N,(int) compsize);
	return 0;
}
