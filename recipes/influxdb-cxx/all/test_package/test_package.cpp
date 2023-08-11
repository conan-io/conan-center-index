#include <InfluxDBFactory.h>

int main()
{
    auto influxdb = influxdb::InfluxDBFactory::Get("http://localhost:8086?db=test");
    influxdb->addGlobalTag("test", "value");
    return 0;
}
