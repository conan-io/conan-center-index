#include <boost/cobalt.hpp>

#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif

boost::cobalt::task<int> task() {
    co_return 0;
}

int main(void) {
    return boost::cobalt::run(task());
}