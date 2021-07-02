#include <iostream>

#include <ois/OIS.h>

int main(int argc, char **argv)
{
    std::cout << "OIS version: " << OIS::InputManager::getVersionNumber() << std::endl;
    return 0;
}
