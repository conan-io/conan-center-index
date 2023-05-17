#include <sqlite3.h>
#include <rasterlite.h>

#include <stdio.h>

int main(void) {
    printf("rasterlite %s\n", rasterliteGetVersion());
    return 0;
}
