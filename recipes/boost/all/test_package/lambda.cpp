#include <boost/lambda/lambda.hpp>
#include <iostream>

int main() {
    using namespace BOOST_NAMESPACE::lambda;
    int x = 1; (_1 = 2)(x);
    std::cout << "Testing Boost::Lambda: " << x << std::endl;
    return 0;
}
