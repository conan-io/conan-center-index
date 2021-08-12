#if ARM_64BIT
# if !defined(__aarch64__)
#  error "__aarch64__ not defined"
# endif
#else
# if !defined(__arm__)
#  error "__arm__ not defined"
# endif
#endif

#include <stdio.h>

int main() {
    printf("hello world\n");
}
