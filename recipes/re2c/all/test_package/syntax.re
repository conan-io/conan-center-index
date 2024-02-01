#include <stdio.h>
#include <assert.h>

/*!include:re2c "unicode_categories.re" */

/*!max:re2c*/
/*!re2c
    digit  = [0-9];
    number = digit+;
    word = L+;
*/

static int lex(const char *YYCURSOR)
{
    const char *YYMARKER;
    /*!re2c
    re2c:flags:utf-8 = 1;
    re2c:define:YYCTYPE = 'unsigned char';
    re2c:yyfill:enable  = 0;

    * { return 1; }

    number {
        printf("number\n");
        return 0;
    }

    word {
        printf("word\n");
        return 0;
    }

    */
}

int main()
{
    assert(lex("1024") == 0);
    assert(lex(";]") == 1);
    assert(lex("Слово") == 0);
    return 0;
}
