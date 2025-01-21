#if defined(__cplusplus) && __cplusplus >= 202002L
using char_type = char8_t;
#else
typedef char char_type;
#endif

#include "utf8.h"

int main()
{
    const char ref[] = {'\xcf', '\xb4', '\xce', '\x98', '\xce',
                        '\x98', '\xce', '\x98', '\0'};
    char str[] = {'\xcf', '\xb4', '\xce', '\xb8', '\xce',
                  '\x98', '\xcf', '\x91', '\0'};

    int r = utf8ncasecmp(reinterpret_cast<const char_type*>(ref), reinterpret_cast<const char_type*>(str), 8);

    return 0;
}
