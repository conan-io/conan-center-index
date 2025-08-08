#include <boost/chrono.hpp>
#include <iostream>

int main()
{
    const auto now = boost::chrono::system_clock::now();
    std::cout << "Current time: " << boost::chrono::system_clock::to_time_t(now) << std::endl;
    return 0;
}
