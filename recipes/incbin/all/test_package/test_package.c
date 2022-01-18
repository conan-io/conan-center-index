#define INCBIN_PREFIX g_
#define INCBIN_STYLE INCBIN_STYLE_SNAKE
#include "incbin.h"

INCBIN(cmake, INCBIN_FILE);

#include <stdio.h>

int main(int argc, char* argv[]) {
    (void)g_cmake_data[0];
    (void)*g_cmake_end;
    printf(INCBIN_FILE" size is %d\n", g_cmake_size);

    return 0;
}
