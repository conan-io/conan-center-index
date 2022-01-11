#include <ryml_std.hpp> // optional header. BUT when used, needs to be included BEFORE ryml.hpp
#include <ryml.hpp>
#include <c4/yml/preprocess.hpp> // needed only for the json sample
#include <c4/format.hpp> // needed only needed for the examples below
#include <c4/fs/fs.hpp>

#include <cstdio>
#include <chrono>

int main() {
    char yml_buf[] = "{foo: 1, bar: [2, 3], john: doe}";
    ryml::Tree tree = ryml::parse_in_place(ryml::substr(yml_buf));

    return EXIT_SUCCESS;
}
