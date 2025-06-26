#include <ultrahdr_api.h>
#include <iostream>

int main()
{
    std::cout << "Creating new decoder " << uhdr_create_decoder() << "\n";
    return 0;
}
