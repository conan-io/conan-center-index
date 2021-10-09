#include <rasterlite2/rasterlite2.h>

#include <stdio.h>

int main(void) {
    printf("rasterlite2 %s\n", rl2_version());
    printf("-- target cpu: %s\n", rl2_target_cpu());
    return 0;
}
