#include <mavsdk/mavsdk.h>
#include <iostream>

using namespace mavsdk;

int main()
{
    Mavsdk mavsdk{Mavsdk::Configuration{1, 180, false}};
    std::cout << "MAVSDK version: " << mavsdk.version() << std::endl;
}
