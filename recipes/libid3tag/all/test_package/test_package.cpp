#include <iostream>
#include <id3tag.h>

int main()
{
    std::cout << "id3tag version: " << id3_version << std::endl;
    std::cout << "id3tag copyright: " << id3_copyright << std::endl;
    std::cout << "id3tag author: " << id3_author << std::endl;
    std::cout << "id3tag build: " << id3_build << std::endl;
    return 0;
}
