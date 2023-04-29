#include <clickhouse/client.h>
#include <clickhouse/error_codes.h>
#include <clickhouse/types/type_parser.h>
#include <clickhouse/base/socket.h>

using namespace clickhouse;

int main()
{
    const auto localHostEndpoint = ClientOptions()
        .SetHost( "localhost")
        .SetPort(9000)
        .SetUser("default")
        .SetPassword("")
        .SetDefaultDatabase("default");
    Client client(ClientOptions(localHostEndpoint));   
    return 0;
}