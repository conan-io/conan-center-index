#include <iostream>
#include <imaGL/imaGL.h>

int main() {
    try {
        imaGL::CImaGL img("notfound.png");
    }
    catch(...) {
    }
    std::cout << "It works!\n";
    return 0;
}
