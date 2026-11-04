#include <sasl/sasl.h>
#include <sasl/saslplug.h>

#include <stdio.h>

int main(int argc, char *argv[])
{
    const char *implementation, *version;
    sasl_version_info(&implementation, &version, NULL, NULL, NULL, NULL);
    printf("--------------------------->Tests are done.<--------------------------\n");
    printf("SASL Using implementation: %s, version: %s\n", implementation, version);
    printf("SASL Utils version: %d\n", SASL_UTILS_VERSION);
    printf("//////////////////////////////////////////////////////////////////////\n");
    return 0;
}
