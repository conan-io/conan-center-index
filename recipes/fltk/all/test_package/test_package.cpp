#include "FL/Fl.H"

#include <iostream>

int main(int argc, char* argv[])
{
    std::cout << "fltk version     : " << Fl::version() << std::endl;
    std::cout << "fltk api version : " << Fl::api_version() << std::endl;
    std::cout << "fltk abi version : " << Fl::abi_version() << std::endl;

    return 0;
}
