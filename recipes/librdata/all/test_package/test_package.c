#include "rdata.h"


int main(int argc, char const *argv[])
{
    rdata_parser_t *parser = rdata_parser_init();
    if (parser == NULL) {
        fprintf(stderr, "Failed to initialize rdata_parser.\n");
        return 1;
    }

    rdata_parser_free(parser);
    printf("librdata is successfully included, linked, and used.\n");

    return 0;
}
