#include <sqlite3.h> // rasterlite.h references things defined in sqlite3.h, but does not include it
#include <rasterlite.h>

#include <stdio.h>

int main(void) {
    printf("rasterlite %s\n", rasterliteGetVersion());
    return 0;
}
