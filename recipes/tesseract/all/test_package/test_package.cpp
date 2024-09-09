#include <tesseract/baseapi.h>

#include <stdio.h>

int main(int argc, char **argv) {
    printf("Tesseract version: %s\n", tesseract::TessBaseAPI::Version());
    return 0;
}

