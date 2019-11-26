#include <iostream>

#include <sodium.h>

int main(void){

    std::cout << "************* Testing libsodium ***************" << std::endl;    

    if (sodium_init() == -1) {
        return 1;
    }
    
    std::cout << "\tOK" << std::endl; 
    std::cout << "***********************************************" << std::endl;   
    
    return 0;
}
