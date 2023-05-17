#include <flann/flann.h>

#include <stdio.h>

int main()
{
    // Simply make sure that it builds an runs
    printf("%i\n", flann_get_distance_type());
    return 0;
}
