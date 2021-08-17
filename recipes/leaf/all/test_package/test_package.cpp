#include <boost/leaf.hpp>
#include <iostream>

namespace leaf = boost::leaf;

int main(int argc, char **argv)
{
    return leaf::try_handle_all(
        [&]() -> leaf::result<int> {
            return 0;
        },
        [](leaf::error_info const &unmatched)
        {
            std::cerr << "Unknown failure detected" << std::endl
                      << "Cryptic diagnostic information follows" << std::endl
                      << unmatched;
            return 6;
        });
}
