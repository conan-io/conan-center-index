#include <cstdlib>
#include <iostream>

#include <embag/view.h>

int main() {
    Embag::View view{};
    // Do not load any bag file for testing
    // view.addBag("xyz.bag");
    const auto start_time = view.getStartTime();
    const auto end_time = view.getEndTime();
    std::cout << "Start time is " << start_time.secs + start_time.nsecs * 1e-9 << std::endl;
    std::cout << "End time is " << end_time.secs + end_time.nsecs * 1e-9 << std::endl;
    for (const auto &message : view.getMessages()) {
        message->print();
    }
    return EXIT_SUCCESS;
}
