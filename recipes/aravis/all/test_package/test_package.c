#include <arv.h>
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv)
{
    printf("Enumerating Aravis interfaces:\n");
    unsigned int if_count = arv_get_n_interfaces();
    for (unsigned int if_index = 0; if_index < if_count; if_index++) {
        const char* if_name = arv_get_interface_id(if_index);
        if (if_name)
            printf("* '%s'\n", if_name);
    }
    arv_shutdown();
    return EXIT_SUCCESS;
}
