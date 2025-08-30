#include <mavsdk.h>

int main()
{
    mavsdk::Mavsdk mavsdk;
    std::string version = mavsdk.version();
    return 0;
}