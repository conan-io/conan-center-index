#include <boost/fiber/all.hpp>
#include <iostream>

int main() {
    BOOST_NAMESPACE::fibers::fiber f([]{ std::cout << "Testing Boost:Fiber" << std::endl; });
    f.join();
    return 0;
}
