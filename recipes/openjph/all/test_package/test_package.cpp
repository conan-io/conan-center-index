#include <openjph/ojph_arch.h>
#include <openjph/ojph_version.h>

#include <iostream>


int main() {
    // Print the version number but also do an API call to check the library
    std::cout << "OpenJPH Version: " << OPENJPH_VERSION_MAJOR << '.' << OPENJPH_VERSION_MINOR << '.' << OPENJPH_VERSION_PATCH << std::endl;
    std::cout << "CPU Extension level: " << ojph::get_cpu_ext_level() << std::endl;

    return EXIT_SUCCESS;
}
