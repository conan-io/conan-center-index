#include "rdata.h"


int main()
{
    rdata_parser_t *parser = rdata_parser_init();
    rdata_parser_free(parser);

    return 0;
}
