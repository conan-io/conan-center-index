#include <boost/process.hpp>

int main()
{
    boost::process::shell().empty();
    return 0;
}
