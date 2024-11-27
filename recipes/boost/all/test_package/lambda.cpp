#include <boost/lambda/lambda.hpp>

int main() {
    using namespace boost::lambda;
    int x = 1; (_1 = 2)(x);
    return 0;
}
