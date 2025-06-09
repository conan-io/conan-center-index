#include <tbb/tbb.h>
#include <iostream>

int main(){
    std::cout << "tbb runtime version: " << TBB_runtime_version() << "\n";
    std::cout << "tbb runtime interface version: " << TBB_runtime_interface_version() << "\n";
    return 0;
}
