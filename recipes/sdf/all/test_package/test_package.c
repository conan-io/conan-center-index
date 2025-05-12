#include "stdio.h"

#define SDF_IMPLEMENTATION
#include "sdf.h"

int main(int argc, char **argv)
{
    unsigned char* dest_data = malloc(0);
    int result = sdfBuildDistanceField(dest_data, 0, 2.0f, NULL, 0, 0, 0);
    printf("Result: %d\n", result);
    printf("Test");

    free(dest_data);

    return 0;
}
