#include <maxminddb.h>
#include <stdio.h>

int main(int argc, char *argv[])
{
    printf("version: %s\n", MMDB_lib_version());
    return 0;
}
