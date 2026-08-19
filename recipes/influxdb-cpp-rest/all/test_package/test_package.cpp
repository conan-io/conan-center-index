#include <influxdb_line.h>
#include <string>

int main()
{
    auto point = influxdb::api::line("measurement",
                                     influxdb::api::key_value_pairs(),
                                     influxdb::api::key_value_pairs("value", 3.14));
    return point.get() == "measurement value=3.14" ? 0 : 1;
}
