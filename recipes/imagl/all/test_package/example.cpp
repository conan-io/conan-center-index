#include <imaGL/imaGL.h>

#include <iostream>

int main() {
    try {
        imaGL::CImaGL img("notfound.png");
    }
    catch(...) {
    }
    std::cout << "It works!\n";
    return 0;
}
