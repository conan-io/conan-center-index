#define MD4QT_ICU_STL_SUPPORT
#include <md4qt/parser.hpp>

#include <memory>
#include <iostream>
#include <filesystem>

int main(int argc, char ** argv)
{
    if (argc < 2) {
        std::cerr << "Need an argument\n";
        return 1;
    }

    MD::Parser< MD::UnicodeStringTrait > parser;

    const auto doc = parser.parse(MD::UnicodeString(argv[1]));

    if(std::static_pointer_cast<MD::Anchor<MD::UnicodeStringTrait>>(doc->items().at(0))->label() ==
        MD::UnicodeString(std::filesystem::canonical(std::filesystem::path(argv[1],
            std::filesystem::path::generic_format)).u8string()))
                return 0;
    else
        return 1;
}
