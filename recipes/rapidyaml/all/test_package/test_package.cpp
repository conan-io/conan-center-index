#include <c4/yml/std/std.hpp>
#include <c4/yml/parse.hpp>
#include <c4/yml/emit.hpp>

#include <iostream>

int main() {
    // `yml::parse() is deprecated since 0.4.0. Use `yml::parse_in_arena()` instead.
#ifdef RYML_USE_PARSE_IN_ARENA
    auto tree = c4::yml::parse_in_arena("{foo: 1}");
#else
    auto tree = c4::yml::parse("{foo: 1}");
#endif

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
