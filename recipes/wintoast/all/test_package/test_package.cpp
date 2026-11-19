#include <cstdlib>
#include <wintoastlib.h>
#include <iostream>

int main()
{
	std::cout << "Compatible?: " << WinToastLib::WinToast::isCompatible() << std::endl;
    return EXIT_SUCCESS;
}
