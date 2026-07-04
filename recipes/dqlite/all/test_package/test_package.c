#include <dqlite.h>
#include <stdio.h>

int main(void)
{
    printf("dqlite version: %s (%d)\n", dqlite_version_string, dqlite_version_number());
    return dqlite_version_number() > 0 ? 0 : 1;
}