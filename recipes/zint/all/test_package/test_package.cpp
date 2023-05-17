#include "qzint.h"

#include <iostream>

#define ZINT_MAJOR(V) (((V)/10000) % 100)
#define ZINT_MINOR(V) (((V)/  100) % 100)
#define ZINT_PATCH(V) (((V)      ) % 100)

int main() {
    Zint::QZint qzint;
    int version = qzint.getVersion();
    std::cout << "zint version: " << ZINT_MAJOR(version) << "." << ZINT_MINOR(version) << "." << ZINT_PATCH(version) << "\n";
}
