#include "libtasn1.h"

#include <stdio.h>

int main (int argc, char *argv[])
{
    ASN1_TYPE PKIX1Implicit88 = ASN1_TYPE_EMPTY;
    if (argc != 2) {
        fprintf(stderr, "Need an argument\n");
        return 1;
    }

    int result;
    char errorDescription[ASN1_MAX_ERROR_DESCRIPTION_SIZE];
    result = asn1_parser2tree(argv[1], &PKIX1Implicit88, errorDescription);

    if (result != ASN1_SUCCESS) {
        asn1_perror (result);
        fprintf(stderr, "asn1error: %s\n", errorDescription);
        return 1;
    }

  return 0;
}
