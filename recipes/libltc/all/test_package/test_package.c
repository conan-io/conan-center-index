/* example was taken from https://www.gnu.org/ghm/2011/paris/slides/andreas-enge-mpc.pdf */

#include <ltc.h>

int main (void) {
    LTCDecoder *decoder = ltc_decoder_create(1920, 1920 * 2);
    ltc_decoder_free(decoder);
    return 0;
}
