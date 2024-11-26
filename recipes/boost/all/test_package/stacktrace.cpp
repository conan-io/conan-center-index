#include <boost/stacktrace.hpp>

#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif

int main() {
    boost::stacktrace::stacktrace().size();
    return 0;
}
