#define MD4QT_ICU_STL_SUPPORT
#ifdef MD4QT_VERSION_GREATER_EQUAL_4
#include <md4qt/parser.h>
#else
#include <md4qt/parser.hpp>
#endif

#include <memory>
#include <iostream>
#include <filesystem>
#include <string>
#include <algorithm>

int main(int argc, char ** argv)
{
    if (argc < 2) {
        std::cerr << "Need an argument\n";
        return 1;
    }

    MD::Parser< MD::UnicodeStringTrait > parser;

    const auto doc = parser.parse(MD::UnicodeString(argv[1]));

    auto path = std::filesystem::canonical(std::filesystem::path(argv[1],
        std::filesystem::path::generic_format)).u8string();
    std::replace( path.begin(), path.end(), '\\', '/' );

    if(std::static_pointer_cast<MD::Anchor<MD::UnicodeStringTrait>>(doc->items().at(0))->label() ==
        MD::UnicodeString(path))
            return 0;
    else
        return 1;
}
