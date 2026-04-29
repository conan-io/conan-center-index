#include <influxdb_line.h>
#include <string>

using namespace influxdb::api;
using namespace std::string_literals;

int main()
{
    std::string result = line("measurement"s, kvpkey_value_pairs("test"s, "value"s)).get();
}
