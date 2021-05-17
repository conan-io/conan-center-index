#include <iostream>
#include <yojimbo.h>

using namespace yojimbo;

int main()
{
    if (!InitializeYojimbo())
    {
        std::cout << "Failed to initialize Yojimbo!\n";
        return 1;
    }
    
    std::cout << "Succesfully initialized Yojimbo\n";
    
    ShutdownYojimbo();
    
    return 0;
}
