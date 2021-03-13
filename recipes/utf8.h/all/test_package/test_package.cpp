#include "utf8.h"

int main()
{
    const char ref[] = {'\xcf', '\xb4', '\xce', '\x98', '\xce',
                        '\x98', '\xce', '\x98', '\0'};
    char str[] = {'\xcf', '\xb4', '\xce', '\xb8', '\xce',
                  '\x98', '\xcf', '\x91', '\0'};

    int r = utf8ncasecmp(ref, str, 8);

    return 0;
}
