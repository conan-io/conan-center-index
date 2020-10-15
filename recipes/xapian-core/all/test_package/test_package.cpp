#include "xapian.h"

#include <iostream>

int main() {
    std::cout << "xapian version " << Xapian::version_string() << "\n";
    return 0;
}
