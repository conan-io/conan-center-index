#include <c4/yml/std/std.hpp>
#include <c4/yml/parse.hpp>
#include <c4/yml/emit.hpp>

#include <iostream>

int main() {
    auto tree = c4::yml::parse("{foo: 1}");
    auto const value = tree["foo"].val();
    
    std::cout << value << std::endl;

    auto bar = tree.rootref()["bar"];
    bar |= c4::yml::SEQ;
    bar.append_child() = "bar0";
    bar.append_child() = "bar1";
    bar.append_child() = "bar2";

    std::string buffer;

    c4::yml::emitrs(tree, &buffer);

    std::cout << buffer << std::endl;

    return EXIT_SUCCESS;
}
