#include <boost/lambda/lambda.hpp>
#include <iostream>
#include <vector>
#include <algorithm>

#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif

int main(int argc, const char * const argv[])
{
    using namespace boost::lambda;

    std::vector<int> values;
    for (int i = 1; i < argc; ++i)
        values.push_back(atoi(argv[i]));

    std::for_each(values.begin(), values.end(), std::cout << _1 * 3 << " " );

    return 0;
}
