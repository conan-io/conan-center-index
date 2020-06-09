#include <iostream>
#include <id3tag.h>

int main()
{
    std::cout << "id3tag version: " << id3_version << std::endl;
    std::cout << "id3tag copyright: " << id3_copyright << std::endl;
    std::cout << "id3tag author: " << id3_author << std::endl;
    std::cout << "id3tag build: " << id3_build << std::endl;

    id3_tag tag;
    id3_tag_version(&tag);

    return 0;
}
