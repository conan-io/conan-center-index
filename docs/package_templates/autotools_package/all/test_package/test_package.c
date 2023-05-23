#include <stdio.h>
#include <stdlib.h>
#include "package/foobar.h" // Make sure includes work as expected


int main(void) {
    printf("Create a minimal usage for the target project here.\n");
    printf("Avoid big examples, bigger than 100 lines\n");
    printf("Avoid networking connections.\n");
    printf("Avoid background apps or servers.\n");
    printf("The propose is testing the generated artifacts only.\n");

    foobar_print_version(); // Make sure to call something that will require linkage for compiled libraries

    return EXIT_SUCCESS;
}
