#include <Platform.Ranges.h>
#include <iostream>

using namespace Platform::Ranges;

int main() {
    try {
        auto range1 = Range(1, 3);
        std::cout << "range1.Minimum: " << range1.Minimum << std::endl;
        std::cout << "range1.Maximum: " << range1.Maximum << std::endl;

        // Attempting to create a range with invalid arguments
        auto range2 = Range(2, 1);
    }
    catch (const std::invalid_argument& e) {
        std::cout << "Exception caught: " << e.what() << std::endl;
    }

    auto range3 = Range(5);
    std::cout << "range3.Minimum: " << range3.Minimum << std::endl;
    std::cout << "range3.Maximum: " << range3.Maximum << std::endl;

    return 0;
}
