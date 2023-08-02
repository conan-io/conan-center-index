#include "mpg123.h"
#include <stdio.h>

int main() {
    int error;
    mpg123_pars *pars;

    pars = mpg123_new_pars(&error);
    mpg123_fmt_all(pars);
    mpg123_delete_pars(pars);
    return 0;
}
