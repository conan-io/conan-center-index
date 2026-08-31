#include <iostream>
#include "Poco/Prometheus/IntCounter.h"

int main() {
    Poco::Prometheus::IntCounter counter("test_counter");
    counter.inc();
    std::cout << "Poco Prometheus: " << counter.value() << std::endl;
    return 0;
}
