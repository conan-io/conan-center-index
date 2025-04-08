#include "plutosvg.h"
#include <stdio.h>

int main(void) {
    plutosvg_document_t* document = plutosvg_document_load_from_file("camera.svg", -1, -1);
    if(document == NULL) {
        printf("Nothing to load\n");
    }

    return 0;
}
