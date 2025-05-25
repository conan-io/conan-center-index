#include <iostream>
#include <suitesparse/cholmod.h>

int main() {
    cholmod_common c;
    cholmod_start(&c);

    std::cout << "SuiteSparse CHOLMOD OK\n";

    cholmod_finish(&c);
    return 0;
}