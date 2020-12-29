#include <openjpeg.h>

#include <cstdlib>
#include <iostream>


int main() {
    std::cout << "opj_has_thread_support: " << opj_has_thread_support() << std::endl;
    std::cout << "opj_get_num_cpus: " << opj_get_num_cpus() << std::endl;

    return EXIT_SUCCESS;
}
