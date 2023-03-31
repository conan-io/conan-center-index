#include <string.h>
#include "linux_syscall_support.h"

#define BUFFER_SIZE 256

int main()
{
    char buffer[BUFFER_SIZE];
    memset(buffer, 0, BUFFER_SIZE);
    int buffer_contains_all_zeros = 0;
    const ssize_t r = sys_getrandom(buffer, BUFFER_SIZE, 0);
    return 0;
}
