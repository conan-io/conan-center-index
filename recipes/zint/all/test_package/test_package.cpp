#include "qzint.h"

#include <iostream>

int main() {
    Zint::QZint qzint;
    std::cout << "Zint version: " << qzint.getVersion() << "\n";
}
