#include <CLI/CLI.hpp>

#include <iostream>

int main(int argc, char **argv) {
    CLI::App app("Test App");
    CLI11_PARSE(app, argc, argv);

    std::cout << app.help() << '\n';
    return 0;
}
