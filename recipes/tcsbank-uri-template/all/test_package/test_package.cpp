#include <iostream>

#include <uri-template/uri-template.h>

int main() {
    const std::string uri = "http://example.com/search?q=cat&lang=en";
    // Parse the template
    const URI::Template::Template uri_template = URI::Template::ParseTemplate("http://example.com/search{?q,lang}");

    // Match it to the URI
    // &matched_values can be nullptr if you don't care about values.
    std::unordered_map<std::string, URI::Template::VarValue> matched_values;
    bool matched = URI::Template::MatchURI(uri_template, uri, &matched_values);

    // Print results
    std::cout << std::boolalpha;
    std::cout << "Template matched: " << matched << std::endl;
    for (const auto& [name, value] : matched_values) {
        std::cout << name << "=" << value << std::endl;
    }

    // Expand
    const std::string expanded_uri = URI::Template::ExpandTemplate(uri_template, matched_values);
    std::cout << "Template expanded: " << expanded_uri << std::endl;
    return 0;
}
