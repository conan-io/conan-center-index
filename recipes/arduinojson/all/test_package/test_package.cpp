#include <ArduinoJson.h>
#include <iostream>

int main(void)
{
    char json[] = "{\"sensor\":\"gps\",\"time\":1351824120,\"data\":[48.756080,2.302038]}";

    DynamicJsonDocument doc(1024);

    deserializeJson(doc, json);

    const char* sensor = doc["sensor"].as<const char*>();
    int time = doc["time"].as<int>();
    double latitude = doc["data"][0].as<double>();
    double longitude = doc["data"][1].as<double>();

    std::cout << "sensor: " << sensor << std::endl;
    std::cout << "time: " << time << std::endl;
    std::cout << "latitude: " << latitude << std::endl;
    std::cout << "longitude: " << longitude << std::endl;

    return 0;
}
