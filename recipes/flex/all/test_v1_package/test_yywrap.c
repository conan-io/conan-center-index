#include <stdio.h>

int yywrap(void);
int yylex(void) {
    return 0;
}

int main() {
    printf("yywrap() returned: %d.\n", yywrap());
}
