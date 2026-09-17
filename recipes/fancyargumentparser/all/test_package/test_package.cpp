#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>

#include <argparse.h>

int main()
{
    argparse::ArgumentParser parser("test_package");
    parser.AddArgument(argparse::CreateNamedArgument(
        "n", "name", 1, argparse::ArgTypeCast::e_String, true));

    auto parsed = parser.ParseArgs(std::vector<std::string>{"--name", "conan"});
    if (!parsed.IsArgValid())
    {
        std::cerr << "parsing failed: " << parsed.GetErrorString() << std::endl;
        return EXIT_FAILURE;
    }

    const std::string name = parsed.GetArg("name").GetAsString();
    std::cout << "parsed name: " << name << std::endl;

    return name == "conan" ? EXIT_SUCCESS : EXIT_FAILURE;
}
