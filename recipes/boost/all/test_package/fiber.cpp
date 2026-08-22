#include <boost/fiber/all.hpp>
#include <iostream>

int main() {
    boost::fibers::fiber f([]{ std::cout << "Testing Boost:Fiber" << std::endl; });
    f.join();
    return 0;
}
