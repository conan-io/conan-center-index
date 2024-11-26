// This comes from the following Boost example:
// https://www.boost.org/doc/libs/1_72_0/doc/html/chrono/users_guide.html#chrono.users_guide.examples
#include <boost/chrono.hpp>

#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif

int main()
{
    boost::chrono::system_clock::time_point start = boost::chrono::system_clock::now();
    return 0;
}
