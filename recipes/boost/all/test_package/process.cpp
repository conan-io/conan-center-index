#include <boost/version.hpp>

#define BOOST_PROCESS_V2_DEFAULT (BOOST_VERSION / 100 % 1000 >= 88)

#ifdef WIN32
// Workaround for https://github.com/boostorg/process/issues/429
// boost/asio/detail/socket_types.hpp(24): fatal error C1189: #error:  WinSock.h has already been included
#include <boost/asio/read.hpp>
#endif

#if BOOST_PROCESS_V2_DEFAULT
#include <boost/process.hpp>
#include <boost/process/shell.hpp>
#else
#include <boost/process/v2.hpp>
#include <boost/process/v2/shell.hpp>
#endif

int main() {
#if BOOST_PROCESS_V2_DEFAULT
    boost::process::shell().empty();
#else
    boost::process::v2::shell().empty();
#endif
    return 0;
}
