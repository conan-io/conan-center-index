#include <iostream>
#include "esc/terminal.hpp"

int main(void) {
    esc::initialize_interactive_terminal();
    esc::uninitialize_terminal();

    std::cout << "terminal size : " << esc::terminal_width() << " x " << esc::terminal_height() << std::endl;
}
