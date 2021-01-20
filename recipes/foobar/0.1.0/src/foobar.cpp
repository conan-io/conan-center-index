#include <iostream>
#include "foobar.h"

void foobar(){
    #ifdef NDEBUG
    std::cout << "foobar/0.1.0: Hello World Release!" <<std::endl;
    #else
    std::cout << "foobar/0.1.0: Hello World Debug!" <<std::endl;
    #endif
}
