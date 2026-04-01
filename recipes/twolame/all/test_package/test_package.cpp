#include <cstdlib>
#include <stdio.h>
#include "twolame.h"

int main(void) {
    printf("Twolame version: %s\n", get_twolame_version());
    printf("Twolame url: %s\n", get_twolame_url());
    return EXIT_SUCCESS;
}

