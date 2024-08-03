#include <toml++/toml.h> // Multiple Headers

#include <fstream> //required for toml::parse_file()
#include <iostream>

using namespace std::string_view_literals;

int main(int argc, char* argv[]) {
    auto config = toml::parse_file(argv[1]);
    // Important: this cast will convert from parse_result which is sometimes defined as a table
    // and sometimes defined as it's own class that is castable to a table&.
    auto& table = static_cast<toml::table&>(config);

    // get key-value pairs
    std::string_view library_name = table["library"]["name"].value_or(""sv);
    std::string_view library_author = table["library"]["authors"][0].value_or(""sv);
    int64_t depends_on_cpp_version = table["dependencies"]["cpp"].value_or(0);

    // modify the data
    table.insert_or_assign("alternatives", toml::array{
        "cpptoml",
        "toml11",
        "Boost.TOML"
    });
    table.insert_or_assign("exceptions", TOML_EXCEPTIONS==1);

    // iterate & visit over the data
    for (auto&& [k, v] : table)
    {
        v.visit([](auto& node) noexcept
        {
            std::cout << node << std::endl;
        });
    }

    // re-serialize as TOML
    std::cout << table << std::endl;

    // re-serialize as JSON
    std::cout << toml::json_formatter{ table } << std::endl;
    return 0;
}
