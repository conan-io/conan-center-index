#include <stdio.h>
#include <atk/atk.h>

int main()
{
    printf("ATK version %d.%d.%d\n",atk_get_major_version(), atk_get_minor_version(), atk_get_micro_version());
    printf("binary age %d\n", atk_get_binary_age());
    printf("interface age %d\n", atk_get_interface_age());
    return 0;
}
