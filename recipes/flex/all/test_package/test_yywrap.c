#include <stdio.h>

int yywrap(void);

int main() {
    printf("yywrap() returned: %d.\n", yywrap());
}
