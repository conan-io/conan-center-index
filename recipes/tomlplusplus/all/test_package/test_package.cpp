#include <toml.hpp>
#include <fstream> //required for toml::parse_file()

int main() {
    auto config = toml::parse_file( "configuration.toml" );

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
            std::cout << node << std:endl;
            if constexpr (toml::is_string<decltype(node)>)
                do_something_with_string_values(node);
        });
    }

    // re-serialize as TOML
    std::cout << config << std::endl;

    // re-serialize as JSON
    std::cout << toml::json_formatter{ config } << std::endl;
    return 0;
}
