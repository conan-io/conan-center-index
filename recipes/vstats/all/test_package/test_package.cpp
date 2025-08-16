#include <vstats/timer.h>
#include <iostream>

int main() {
    vstats::Timer timer;
    timer.start();
    // Simulate some work
    for (volatile int i = 0; i < 1000000; ++i);
    timer.stop();
    std::cout << "Elapsed: " << timer.elapsed() << " ms\n";
    return 0;
}
