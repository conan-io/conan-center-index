#include <cstdlib>

#include <faiss/utils/utils.h>
#include <iostream>


int main(void) {

    std::cout << "FAISS VERSION: " << faiss::get_version() << std::endl;
    return EXIT_SUCCESS;
}
