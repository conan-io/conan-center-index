#include <lmdb.h>
#include <stdio.h>
#include <stdlib.h>

int main()
{
    const char *version = mdb_version(NULL, NULL, NULL);
    printf("%s\n", version);
    return 0;
}
