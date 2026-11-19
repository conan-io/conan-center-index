#include "mpg123.h"
#ifdef _MSC_VER
/* Older syn123.h headers use ssize_t, which MSVC lacks. */
#include <stddef.h>
typedef ptrdiff_t ssize_t;
#endif
#include "syn123.h"
#include <stdio.h>

int main() {
    int error;
    mpg123_pars *pars;
    syn123_handle *synth;

    pars = mpg123_new_pars(&error);
    mpg123_fmt_all(pars);
    mpg123_delete_pars(pars);

    synth = syn123_new(44100, 1, MPG123_ENC_SIGNED_16, 0, &error);
    if (!synth)
        return 1;
    syn123_del(synth);
    return 0;
}
