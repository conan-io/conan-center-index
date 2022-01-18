#include <llhttp.h>

#include <stdio.h>

int main()
{
    unsigned major = LLHTTP_VERSION_MAJOR;
    unsigned minor = LLHTTP_VERSION_MINOR;
    unsigned patch = LLHTTP_VERSION_PATCH;
    printf("llhttp v%u.%u.%u\n", major, minor, patch);
    printf("Sample function call: "
           "llhttp_method_name(llhttp_method::HTTP_GET) = \"%s\"...\n",
           llhttp_method_name(HTTP_GET) );

    return 0;
}
