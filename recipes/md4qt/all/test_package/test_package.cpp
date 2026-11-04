#include <md4qt/parser.h>

#include <iostream>
#include <filesystem>
#include <algorithm>

int main(int argc, char ** argv)
{
    if (argc < 2) {
        std::cerr << "Need an argument\n";
        return 1;
    }

    MD::Parser parser;

    const auto doc = parser.parse(QString(argv[1]));

    auto path = std::filesystem::canonical(std::filesystem::path(argv[1],
        std::filesystem::path::generic_format)).string();
    std::replace( path.begin(), path.end(), '\\', '/' );

    if(doc->items().at(0).staticCast<MD::Anchor>()->label() == QString::fromStdString(path))
        return 0;
    else
        return 1;
}
