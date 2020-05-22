#include <boost/regex.hpp>
#ifdef USE_ICU
#include <boost/regex/icu.hpp>
#endif
#include <iostream>

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

    bool result = true;
#ifdef USE_ICU
    result &= boost::u32regex_match( "Is icu 図書館 there ?", boost::make_u32regex( ".*書.*" ) );
#endif
    return ! result;

}
