#include "influxdb.hpp"

int main()
{
    influxdb_cpp::server_info si("127.0.0.1", 8086, "testx", "test", "test");
}
