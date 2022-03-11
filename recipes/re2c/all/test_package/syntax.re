#include <stdio.h>

/*!max:re2c*/
/*!re2c
    digit  = [0-9];
    number = digit+;
*/

static int lex(const char *YYCURSOR)
{
    const char *YYMARKER;
    /*!re2c
    re2c:define:YYCTYPE = char;
    re2c:yyfill:enable  = 0;

    * { return 1; }

    number {
        printf("number\n");
        return 0;
    }

    */
}

int main()
{
    lex("1024");
    lex(";]");
    return 0;
}
