#include "wolfssl/ssl.h"

int main()
{
    wolfSSL_Init();
    wolfSSL_Cleanup();
    return 0;
}
