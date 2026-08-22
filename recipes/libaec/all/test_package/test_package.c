#include <stdint.h>
#include <libaec.h>

/* Modified from the encoding example in the readme */

int main(void) {
    struct aec_stream strm;
    size_t source_length = 1024;
    size_t dest_length = 4096;
    int32_t source[1024];
    unsigned char dest[4096];
    size_t idx;

    for(idx=0;idx<source_length;idx++) {
        source[idx] = (int32_t)idx;
    }

    /* input data is 32 bits wide */
    strm.bits_per_sample = 32;

    /* define a block size of 16 */
    strm.block_size = 16;

    /* the reference sample interval is set to 128 blocks */
    strm.rsi = 128;

    /* input data is signed and needs to be preprocessed */
    strm.flags = AEC_DATA_SIGNED | AEC_DATA_PREPROCESS;

    /* pointer to input */
    strm.next_in = (unsigned char *)source;

    /* length of input in bytes */
    strm.avail_in = source_length * sizeof(int32_t);

    /* pointer to output buffer */
    strm.next_out = dest;

    /* length of output buffer in bytes */
    strm.avail_out = dest_length;

    /* initialize encoding */
    if (aec_encode_init(&strm) != AEC_OK)
        return 1;

    /* Perform encoding in one call and flush output. */
    /* In this example you must be sure that the output */
    /* buffer is large enough for all compressed output */
    if (aec_encode(&strm, AEC_FLUSH) != AEC_OK)
        return 1;

    /* free all resources used by encoder */
    aec_encode_end(&strm);
    return 0;
}
