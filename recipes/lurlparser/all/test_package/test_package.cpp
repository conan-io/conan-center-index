#include <iostream>

#include "LUrlParser.h"

int main() {
    const auto URL = LUrlParser::ParseURL::parseURL("https://John:Dow@github.com:80/corporateshark/LUrlParser");

    if (URL.isValid()) {
        std::cout << "Scheme    : " << URL.scheme_ << std::endl;
        std::cout << "Host      : " << URL.host_ << std::endl;
        std::cout << "Port      : " << URL.port_ << std::endl;
        std::cout << "Path      : " << URL.path_ << std::endl;
        std::cout << "Query     : " << URL.query_ << std::endl;
        std::cout << "Fragment  : " << URL.fragment_ << std::endl;
        std::cout << "User name : " << URL.userName_ << std::endl;
        std::cout << "Password  : " << URL.password_ << std::endl;
    }

    return 0;
}
