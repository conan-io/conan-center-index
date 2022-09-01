#include <stdio.h>
#include <stdlib.h>
#include "package/foobar.p"


int main(void) {
    printf("Create a minimal usage for the target project here.\n");
    printf("Avoid big examples, bigger than 100 lines\n");
    printf("Avoid networking connections.\n");
    printf("Avoid background apps or servers.\n");
    printf("The propose is testing the generated artifacts only.\n");

    foobar_print_version();

    return EXIT_SUCCESS;
}
