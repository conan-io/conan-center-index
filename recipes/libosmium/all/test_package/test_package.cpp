#include <osmium/io/any_input.hpp>

#include <iostream>

int main() {
    try {
        const osmium::io::File input_file{"missing_file.pbf"};
        osmium::io::Reader reader{input_file};
    } catch (const std::exception& e) {
        std::cerr << e.what() << '\n';
        return 0;
    }
}
