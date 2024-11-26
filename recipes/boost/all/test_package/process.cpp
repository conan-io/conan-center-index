#include <boost/process.hpp>

#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif


int main()
{
    boost::process::shell().empty();
    return 0;
}
