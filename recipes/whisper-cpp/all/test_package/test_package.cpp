#include <iostream>
#include <whisper.h>

int main() {
    std::cout << whisper_print_system_info() << std::endl;
    return 0;
}
