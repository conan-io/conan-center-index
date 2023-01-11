#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "lsqpack.h"

int
lsqpack_dec_int (const unsigned char **src_p, const unsigned char *src_end,
                 unsigned prefix_bits, uint64_t *value_p,
                 struct lsqpack_dec_int_state *state);


struct int_test
{
    int             it_lineno;
    unsigned        it_prefix_bits;
    unsigned char   it_encoded[20];
    size_t          it_enc_sz;
    uint64_t        it_decoded;
    int             it_dec_retval;
};

static const struct int_test tests[] =
{

    {   .it_lineno      = __LINE__,
        .it_prefix_bits = 7,
        .it_encoded     = { 0x7F, 0x02, },
        .it_enc_sz      = 2,
        .it_decoded     = 0x81,
        .it_dec_retval  = 0,
    },
};

int
main (void)
{
    struct lsqpack_enc enc;
    size_t dec_sz;
    int s;
    unsigned i;
    const unsigned char *p;
    uint64_t val;
    struct lsqpack_dec_int_state state;
    unsigned char dec_buf[LSQPACK_LONGEST_SDTC];

    const struct {
        unsigned    peer_max_size;  /* Value provided by peer */
        unsigned    our_max_size;   /* Value to use */
        int         expected_tsu;   /* Expecting TSU instruction? */
    } tests[] = {
        {   0x1000,     0x1000,     1,  },
        {   0x1000,     1,          1,  },
        {    0x100,     0x100,      1,  },
        {   0x1000,     0,          0,  },
    };

    for (i = 0; i < sizeof(tests) / sizeof(tests[0]); ++i)
    {
        dec_sz = sizeof(dec_buf);
        s = lsqpack_enc_init(&enc, stderr, tests[i].peer_max_size,
                        tests[i].our_max_size, 0, 0, dec_buf, &dec_sz);
        assert(s == 0);
        if (tests[i].expected_tsu)
        {
            assert(dec_sz > 0);
            assert((dec_buf[0] & 0xE0) == 0x20);
            p = dec_buf;
            state.resume = 0;
            s = lsqpack_dec_int(&p, p + dec_sz, 5, &val, &state);
            assert(s == 0);
            assert(val == tests[i].our_max_size);
        }
        else
            assert(dec_sz == 0);
        lsqpack_enc_cleanup(&enc);
    }
    return 0;
}
