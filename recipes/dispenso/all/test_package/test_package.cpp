#include <iostream>
#include "dispenso/parallel_for.h"


int main(void) {
    dispenso::parallel_for(0, 5, [] (size_t j) {
        std::cout << j << std::endl;
   });
}
