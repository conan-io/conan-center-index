#include <cstdlib>
#include <iostream>

#include "base/time/time.h"

int main() {
    const auto now = base::Time::Now();
    std::cout << "Libbase - Current time: " << now.ToTimeT() << " seconds since the Unix epoch." << std::endl;
    return EXIT_SUCCESS;
}
