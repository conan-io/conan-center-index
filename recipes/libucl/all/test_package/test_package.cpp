#include "ucl++.h"

#include <fstream>
#include <iostream>
#include <string>

int main(int argc, char *argv[])
{
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << "  FILE\n";
        return 1;
    }
    std::string input, err;

    std::ifstream ifs(argv[1]);
    input.assign(std::istreambuf_iterator<char>(ifs), std::istreambuf_iterator<char>());

    auto obj = ucl::Ucl::parse(input, err);

    if (obj) {
        std::cout << "input config is:\n";
        std::cout << obj.dump(UCL_EMIT_CONFIG) << std::endl;
        std::cout << "======\n";

        for (const auto &o : obj) {
            std::cout << "obj: " << o.dump(UCL_EMIT_CONFIG) << std::endl;
        }
    }
    else {
        std::cerr << "error: " << err << std::endl;
        return 1;
    }
    return 0;
}
