#include <clocale>
#include <cstdlib>
#include <iostream>

#include "libintl.h"

int main() {
    setlocale(LC_ALL, "");
    std::cout << gettext("Hello, world!") << std::endl;
    return EXIT_SUCCESS;
}