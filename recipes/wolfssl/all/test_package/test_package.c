#include "wolfssl/ssl.h"

int main(void)
{
    wolfSSL_Init();
    wolfSSL_Cleanup();
    return 0;
}
