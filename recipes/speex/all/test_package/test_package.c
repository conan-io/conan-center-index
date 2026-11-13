#include <speex/speex.h>

int main(void) {
    const SpeexMode *mode = speex_lib_get_mode(SPEEX_MODEID_NB);
    return mode ? 0 : 1;
}
