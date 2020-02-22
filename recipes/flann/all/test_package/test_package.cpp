#include <iostream>
#include <flann/flann.h>

int main()
{
    // Simply make sure that it builds an runs
    std::cout << flann_get_distance_type() << '\n';
}
