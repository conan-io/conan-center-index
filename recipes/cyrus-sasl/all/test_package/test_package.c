#include <sasl/sasl.h>

#include <stdio.h>

int main(int argc, char *argv[])
{
    const char *implementation, *version;
    sasl_version_info(&implementation, &version, NULL, NULL, NULL, NULL);
    printf("--------------------------->Tests are done.<--------------------------\n");
    printf("SASL Using implementation: %s, version: %s\n", implementation, version);
    printf("//////////////////////////////////////////////////////////////////////\n");
    return 0;
}
