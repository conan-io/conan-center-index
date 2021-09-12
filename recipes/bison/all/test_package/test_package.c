#include <stdio.h>

int yyerror(const char *msg);

int main()
{
    char error[] = "conan-center-index";
    printf("%d\n", yyerror(error));
    return 0;
}
