#include <iostream>

#define RND_IMPLEMENTATION
#include "rnd.h"

int main()
{

    rnd_pcg_t pcg;
    rnd_pcg_seed(&pcg, 0u); // initialize generator

    std::cout << rnd_pcg_next(&pcg) << std::endl;

    return 0;
}
