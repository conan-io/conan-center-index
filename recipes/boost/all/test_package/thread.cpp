#include <boost/thread.hpp>
#include <iostream>

#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif

int main(int argc, const char * const argv[])
{
    boost::thread thread([](){ std::cout << "Thread has been created\n"; });
    thread.join();
    return 0;
}
