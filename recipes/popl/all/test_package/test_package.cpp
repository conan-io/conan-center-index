#include <popl.hpp>

#include <iostream>

using namespace popl;

int main(int argc, char **argv) {
    OptionParser op("Allowed options");
    auto help_option = op.add<Switch>("h", "help", "produce help message");
    op.parse(argc, argv);
    std::cout << op << "\n";
}
