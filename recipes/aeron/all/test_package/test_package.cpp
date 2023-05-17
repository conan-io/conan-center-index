#include <Aeron.h>

#include <cstdlib>
#include <iostream>


int main()
{
    std::cout << "Aeron: " << ::aeron::Aeron::version() << std::endl;
    return EXIT_SUCCESS;
}
