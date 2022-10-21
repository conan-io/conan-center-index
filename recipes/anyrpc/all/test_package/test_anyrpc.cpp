#include <cstdlib>
#include <iostream>

#include "anyrpc/anyrpc.h"

int main(void)
{
    anyrpc::JsonHttpServer server;
    std::cout << "Success!" << std::endl;

    return EXIT_SUCCESS;
}
