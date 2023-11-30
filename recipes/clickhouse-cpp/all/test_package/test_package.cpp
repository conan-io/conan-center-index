#include <clickhouse/client.h>
#include <clickhouse/error_codes.h>
#include <clickhouse/types/type_parser.h>
#include <clickhouse/base/socket.h>

#include <iostream>
#include <stdexcept>
using namespace clickhouse;

int main()
{
    const auto localHostEndpoint = ClientOptions()
        .SetHost( "localhost")
        .SetPort(9000)
        .SetUser("default")
        .SetPassword("")
        .SetDefaultDatabase("default");

    try {
        Client client(localHostEndpoint); 
    }
    catch (const std::exception &ex)
    {
        std::cout << "not connected but works" << std::endl;
    }
      
    return 0;
}
