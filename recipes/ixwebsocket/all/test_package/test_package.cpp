#include <iostream>
#include <ixwebsocket/IXUrlParser.h>

int main() {
    std::string url = "https://github.com";
    std::string protocol, host, path, query;
    int port;

    bool res = ix::UrlParser::parse(url, protocol, host, path, query, port);

    std::cout
        << "URL parse result: \n"
        << "Protocol: " << protocol
        << "\nHost: " << host
        << "\nPath: " << path
        << "\nQuery: " << query
        << "\nPort: " << port << std::endl;
}
