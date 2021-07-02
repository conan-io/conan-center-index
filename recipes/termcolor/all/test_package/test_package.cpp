#include <termcolor/termcolor.hpp>

#include <iostream>

int main(int /*argc*/, char** /*argv*/)
{
    std::cout << termcolor::red << termcolor::on_white << "Hello, ";
    std::cout << termcolor::reset << termcolor::blink << termcolor::green << "Colorful ";
    std::cout << termcolor::reset << termcolor::underline << termcolor::blue << "World!";
    std::cout << std::endl << termcolor::reset;
    return 0;
}
