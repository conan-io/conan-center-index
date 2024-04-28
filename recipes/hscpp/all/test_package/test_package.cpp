#include <hscpp/Hotswapper.h>

class Demo {};

int main()
{
    hscpp::Hotswapper swapper;
    Demo demo;
    swapper.SetGlobalUserData(&demo);
}
