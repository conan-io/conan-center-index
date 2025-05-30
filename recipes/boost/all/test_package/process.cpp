#include <boost/version.hpp>

#define BOOST_PROCESS_V2_DEFAULT (BOOST_VERSION / 100 % 1000 >= 88)

#if BOOST_PROCESS_V2_DEFAULT
#include <boost/process/v2.hpp>
#else
#include <boost/process.hpp>
#endif

int main()
{
#if BOOST_PROCESS_V2_DEFAULT
    boost::process::v2::shell().empty();
#else
    boost::process::shell().empty();
#endif
    return 0;
}
