#include <boost/nowide/args.hpp>
#include <iostream>

int main(int argc,char **argv)
{
    boost::nowide::args args(argc,argv);
    std::cout << "Testing Boost::Nowide: " << args.argc() << std::endl;
    return 0;
}
