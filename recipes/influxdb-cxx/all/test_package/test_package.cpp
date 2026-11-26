#include <InfluxDB/InfluxDBFactory.h>
#include <InfluxDB/InfluxDBException.h>
#include <iostream>

int main()
{
    try {
        auto influxdb = influxdb::InfluxDBFactory::Get("xyz://foobar");
    }
    catch(influxdb::InfluxDBException& e) {

    }

    std::cout << "Influxdb-cxx test package successful\n";
    return 0;
}
