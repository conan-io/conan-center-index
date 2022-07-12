#include <stdio.h>
#include <stdlib.h>

#if STC_VERSION == 1

#include <stc/cvec.h>
using_cvec(i, int);

int main(void) {
    cvec_i vec = cvec_i_init();
    cvec_i_push_back(&vec, 10);
    cvec_i_push_back(&vec, 20);
    cvec_i_push_back(&vec, 30);

    c_foreach (i, cvec_i, vec)
        printf(" %d", *i.ref);

    cvec_i_del(&vec);

    return EXIT_SUCCESS;
}

#elif STC_VERSION == 3

#define i_val int
#define i_tag i
#include <stc/cvec.h>

int main(void) {
    cvec_i vec = cvec_i_init();
    cvec_i_push_back(&vec, 10);
    cvec_i_push_back(&vec, 20);
    cvec_i_push_back(&vec, 30);

    c_foreach (i, cvec_i, vec)
        printf(" %d", *i.ref);

    cvec_i_drop(&vec);

    return EXIT_SUCCESS;
}

#else
#error "invalid STC_VERSION"
#endif
