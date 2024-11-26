#include <boost/fiber/all.hpp>

#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif

int main() {
    boost::fibers::fiber f([]{});
    f.join();
    return 0;
}
