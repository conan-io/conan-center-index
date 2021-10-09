#include <boost/regex.hpp>
#include <iostream>

#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif

int main(int argc, const char * const argv[])
{
    std::string line;
    boost::regex pat( "^Subject: (Re: |Aw: )*(.*)" );

    std::vector<int> values;
    for (int i = 1; i < argc; ++i) {
        const std::string word(argv[i]);
        boost::smatch matches;
        if (boost::regex_match(line, matches, pat))
            std::cout << matches[2] << std::endl;
    }
}
