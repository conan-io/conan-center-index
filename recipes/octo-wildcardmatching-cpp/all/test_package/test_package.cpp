#include "octo-wildcardmatching-cpp/wildcard-path-matcher.hpp"
#include <iostream>

int main(int argc, char** argv)
{
    octo::wildcardmatching::WildcardPathMatcher path_matcher;
    path_matcher.add_wildcard_path("/usr/**/*.so");
    auto match = path_matcher.get_wildcard_match("/usr/lib64/security/pam.so");
    std::cout << match << std::endl;
}
