#include <orcania.h>
#include <stdio.h>
#include <stdlib.h>

int main() {
    const char *mystring = "Hello world!";
    char* str2 = o_strdup(mystring);
    puts(str2);
    free(str2);
    return 0;
}
