#include "clara.hpp"

#include <iostream>

static void printHelp(const clara::Parser &cli) {
    auto columns = cli.getHelpColumns();
    for (const auto &column : columns) {
        std::cout << column.left << '\t' << column.right << '\n';
    }
}

int main(int argc, const char * argv []) {
    int width = 0;
    bool help = false;
    auto cli = clara::Opt( width, "width" )
        ["-w"]["--width"]
        ("How wide should it be?")
        | clara::Help(help);
    auto result = cli.parse( clara::Args( argc, argv ) );
    if (!result) {
        std::cerr << "Error in command line: " << result.errorMessage() << std::endl;
        printHelp(cli);
        return 1;
    }
    if (help) {
        printHelp(cli);
        return 0;
    }
    std::cout << "width is " << width << '\n';
    return 0;
}
