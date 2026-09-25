#include <boost/chrono.hpp>
#include <iostream>

int main()
{
    const auto now = BOOST_NAMESPACE::chrono::system_clock::now();
    std::cout << "Current time: " << BOOST_NAMESPACE::chrono::system_clock::to_time_t(now) << std::endl;
    return 0;
}
