#include <jsonv/parse.hpp>
#include <jsonv/value.hpp>

#include <cstdlib>
#include <iostream>

int main()
{
    jsonv::value doc = jsonv::parse(R"({"name": "jsonv", "version": [2, 0, 0]})");
    std::cout << doc << std::endl;
    return doc.at("version").at(0).as_integer() == 2 ? EXIT_SUCCESS : EXIT_FAILURE;
}
