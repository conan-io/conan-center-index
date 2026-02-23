#include <tomcrypt.h>

int main(void)
{
    const char *msg = error_to_string(CRYPT_OK);
    return (msg != 0) ? 0 : 1;
}
