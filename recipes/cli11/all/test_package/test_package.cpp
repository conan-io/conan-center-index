#include <CLI/CLI.hpp>
#include <iostream>
#include <string>

int main(int argc, char **argv) {
    int count{0};
    int v{0};
    double value{0.0};  // = 3.14;
    std::string file;
    CLI::App app("K3Pi goofit fitter");

    CLI::Option *opt = app.add_option("-f,--file,file", file, "File name");
    CLI::Option *copt = app.add_option("-c,--count", count, "Counter");
    CLI::Option *flag = app.add_flag("--flag", v, "Some flag that can be passed multiple times");

    app.add_option("-d,--double", value, "Some Value");
    CLI11_PARSE(app, argc, argv);

    std::cout << "Working on file: " << file << ", direct count: " << app.count("--file")
              << ", opt count: " << opt->count() << std::endl;
    std::cout << "Working on count: " << count << ", direct count: " << app.count("--count")
              << ", opt count: " << copt->count() << std::endl;
    std::cout << "Received flag: " << v << " (" << flag->count() << ") times\n";
    std::cout << "Some value: " << value << std::endl;

    return 0;
}
