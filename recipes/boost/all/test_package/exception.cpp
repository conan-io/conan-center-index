#include <boost/exception/all.hpp>
#include <iostream>

typedef boost::error_info<struct tag_my_info,int> my_info;

struct my_error: virtual boost::exception, virtual std::exception { };

void throw_exception()
{
    throw my_error() << my_info(42);
}

int main(int argc, const char * const argv[])
{
    try
    {
        throw_exception();
    }
    catch(my_error & x )
    {
        if (int const * mi = boost::get_error_info<my_info>(x))
        {
            std::cerr << "My info: " << *mi;
        }
    }
}
