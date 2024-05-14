#include <iostream>

#include <artery-font/structures.h>

int main(int argc, char *argv[]) {
    artery_font::KernPair<float> kp;
    kp.codepoint1 = 65; // ASCII value for 'A'
    kp.codepoint2 = 66; // ASCII value for 'B'
    kp.advance.h = 1.0f;
    kp.advance.v = 0.0f;
    std::cout << "Test: " << sizeof(kp) << std::endl;

    return EXIT_SUCCESS;
}
