#include <iostream>
#include <mad.h>

int main()
{
    std::cout << "mad version: " << mad_version << std::endl;
    std::cout << "mad copyright: " << mad_copyright << std::endl;
    std::cout << "mad author: " << mad_author << std::endl;
    std::cout << "mad build: " << mad_build << std::endl;
    return 0;
}
