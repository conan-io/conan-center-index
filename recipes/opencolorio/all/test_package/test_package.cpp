#include <OpenColorIO/OpenColorIO.h>
#include <iostream>

int main()
{
    std::cout << "OpenColorIO " << OCIO_NAMESPACE::GetVersion() << "\n";
    return 0;
}
