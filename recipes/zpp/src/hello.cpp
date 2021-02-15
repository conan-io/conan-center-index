#include <iostream>
#include "hello.h"

void hello(){
    #ifdef NDEBUG
    std::cout << "zpp release" <<std::endl;
    #else
    std::cout << "zpp debug!" <<std::endl;
    #endif
}
