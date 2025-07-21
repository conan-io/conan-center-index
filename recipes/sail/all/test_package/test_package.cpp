#include <iostream>

#include <sail-c++/sail-c++.h>

int main(int argc, char *argv[])
{
    const char* filename = "my-binary.bmp";
    try {
        const sail::image image(filename);
        std::cout << "Size: " << image.width() << '\n'; // Never reached
    } catch (const std::exception& e) {
        std::cout << "Tried to open " << filename << " with sail library\n";
    }
    std::cout << "TEST SUCCEED\n";

    return 0;
}
