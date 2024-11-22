#include <util/io-redirector.h>
#include <util/ities.h>
#include <iostream>

int main() {
    util::IoRedirector::get();
    std::cout << "scc loaded successfully. Mini test: util::ilog2(32) = " << util::ilog2(32) << std::endl;
    return 0;
}
