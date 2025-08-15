// Standard headers
#include <stdio.h>

// sbgECom headers
#include <sbgEComGetVersion.h>

// Main entrypoint
int main()
{
    printf("Using sbgECom version '%s'\n", sbgEComGetVersionAsString());
    return 0;
}
