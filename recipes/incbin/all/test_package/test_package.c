#define INCBIN_PREFIX g_
#define INCBIN_STYLE INCBIN_STYLE_SNAKE
#include <incbin.h>

#include <stdio.h>

INCBIN(hello_world, "hello_world.txt");

int main(int argc, char* argv[]) {
    fwrite(g_hello_world_data, 1, g_hello_world_size, stdout);
    return 0;
}
