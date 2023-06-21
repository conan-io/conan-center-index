#include <rtklib.h>

#include <cstdlib>
#include <iostream>

int main() {
    int week = 0;
    double sec = time2gpst(timeget(), &week);
    std::cout << "Current GPS time: week " << week << ", " << sec << " seconds of week" << std::endl;
    return EXIT_SUCCESS;
}
