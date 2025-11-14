#include <influxdb_line.h>
#include <iostream>
#include <string>

using namespace influxdb::api;
using namespace std::string_literals;

int main()
{
    // Test that we can construct key_value_pairs with various types
    auto kvp_string = key_value_pairs("tag1"s, "value1"s);
    auto kvp_int = key_value_pairs("int_field"s, 42);
    auto kvp_long = key_value_pairs("long_field"s, 123L);
    auto kvp_double = key_value_pairs("double_field"s, 3.14);
    auto kvp_bool = key_value_pairs("bool_field"s, true);
    
    // Test chaining
    auto kvp_multi = key_value_pairs("a"s, "b"s)
        .add("b"s, 42)
        .add("c"s, 33.01);
    
    // Test line construction with tags and fields
    auto test_line = line("measurement"s, kvp_string, kvp_int);
    
    // Test line with multiple fields
    auto line_multi = line("test_measurement"s,
        key_value_pairs("tag1"s, "tag_value1"s),
        key_value_pairs("field1"s, 100).add("field2"s, "hello"s).add("field3"s, 45.67));
    
    // Verify the lines can be formatted
    std::string line1_str = test_line.get();
    std::string line2_str = line_multi.get();
    std::string kvp_str = kvp_multi.get();
    
    if (line1_str.empty() || line2_str.empty() || kvp_str.empty()) {
        std::cerr << "Error: Generated strings are empty\n";
        return 1;
    }
    
    // Verify basic formatting structure
    if (line1_str.find("measurement") == std::string::npos) {
        std::cerr << "Error: Measurement name not found in line\n";
        return 1;
    }
    
    std::cout << "influxdb-cpp-rest test package successful\n";
    std::cout << "Generated line 1: " << line1_str << "\n";
    std::cout << "Generated line 2: " << line2_str << "\n";
    std::cout << "Generated kvp: " << kvp_str << "\n";
    
    return 0;
}

