#include <boost/version.hpp>
#include <boost/process.hpp>

#define BOOST_PROCESS_V2_DEFAULT (BOOST_VERSION / 100 % 1000 >= 88)

int main() {
#if BOOST_PROCESS_V2_DEFAULT
    boost::process::v2::shell().empty();
#else
    boost::process::shell().empty();
#endif
    return 0;
}
