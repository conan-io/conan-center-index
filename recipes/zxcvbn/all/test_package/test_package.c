#include <zxcvbn.h>

int main(void) {
    ZxcvbnMatch("password", NULL, NULL);

    return EXIT_SUCCESS;
}
