#include <stdio.h>
#include "cbor.h"

int main(int argc, char *argv[])
{
    CborParser parser;
    CborValue it;
    size_t length;
    uint8_t *buf;
    CborError err = cbor_parser_init(buf, length, 0, &parser, &it);

    printf("Tinycbor test_package ran successfully \n");
    return 0;
}