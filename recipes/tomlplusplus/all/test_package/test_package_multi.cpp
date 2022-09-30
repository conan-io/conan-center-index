#include <toml++/toml.h> // Multiple Headers

#include <fstream> //required for toml::parse_file()
#include <iostream>

using namespace std::string_view_literals;

int main(int argc, char* argv[]) {
    auto config = toml::parse_file(argv[1]);

    // get key-value pairs
    std::string_view library_name = config["library"]["name"].value_or(""sv);
    std::string_view library_author = config["library"]["authors"][0].value_or(""sv);
    int64_t depends_on_cpp_version = config["dependencies"]["cpp"].value_or(0);

    // modify the data
    config.insert_or_assign("alternatives", toml::array{
        "cpptoml",
        "toml11",
        "Boost.TOML"
    });

    // iterate & visit over the data
    for (auto&& [k, v] : config)
    {
        v.visit([](auto& node) noexcept
        {
            std::cout << node << std::endl;
        });
    }

    // re-serialize as TOML
    std::cout << config << std::endl;

    // re-serialize as JSON
    std::cout << toml::json_formatter{ config } << std::endl;
    return 0;
}
