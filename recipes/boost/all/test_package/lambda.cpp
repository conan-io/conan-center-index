#include <boost/lambda/lambda.hpp>


#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif

int main() {
    using namespace boost::lambda;
    int x = 1; (_1 = 2)(x);
    return 0;
}
