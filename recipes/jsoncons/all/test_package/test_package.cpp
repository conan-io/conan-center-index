#include <jsoncons/json.hpp>
#include <jsoncons_ext/jsonpath/jsonpath.hpp>
#include <iostream>

using namespace jsoncons; // for convenience

std::string data = R"(
    {
       "application": "hiking",
       "reputons": [
       {
           "rater": "HikingAsylum",
           "assertion": "advanced",
           "rated": "Marilyn C",
           "rating": 0.90,
           "generated": 1514862245
         }
       ]
    }
)";

int main()
{
    // Parse the string of data into a json value
    json j = json::parse(data);

    // Does object member reputons exist?
    std::cout << "(1) " << std::boolalpha << j.contains("reputons") << "\n\n";

    // Get a reference to reputons array 
    const json& v = j["reputons"]; 

    // Iterate over reputons array 
    std::cout << "(2)\n";
    for (const auto& item : v.array_range())
    {
        // Access rated as string and rating as double
        std::cout << item["rated"].as<std::string>() << ", " << item["rating"].as<double>() << "\n";
    }
    std::cout << "\n";

    // Select all "rated" with JSONPath
    std::cout << "(3)\n";
    json result = jsonpath::json_query(j,"$..rated");
    std::cout << pretty_print(result) << "\n\n";

    // Serialize back to JSON
    std::cout << "(4)\n" << pretty_print(j) << "\n\n";
}
