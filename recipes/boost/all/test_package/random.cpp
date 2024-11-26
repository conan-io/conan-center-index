#include <boost/random.hpp>

#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif

int main() {
    boost::random::mt19937 rng;
    boost::random::uniform_int_distribution<>(1, 100)(rng);
    return 0;
}
