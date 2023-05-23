#include <http_parser.h>

#include <stdio.h>

int main()
{
    unsigned long version = http_parser_version();
    unsigned major = (version >> 16) & 255;
    unsigned minor = (version >> 8) & 255;
    unsigned patch = version & 255;
    printf("http_parser v%u.%u.%u\n", major, minor, patch);
    return 0;
}
