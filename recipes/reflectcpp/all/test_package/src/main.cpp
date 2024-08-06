#include <rfl.hpp>
#include <rfl/json.hpp>
#include <string>
#include <vector>

int main(int argc, char** argv) {
    using Age =
        rfl::Validator<unsigned int, rfl::Minimum<0>, rfl::Maximum<130>>;

    struct Person {
        rfl::Rename<"firstName", std::string> first_name;
        rfl::Rename<"lastName", std::string> last_name = "Simpson";
        std::string town = "Springfield";
        rfl::Timestamp<"%Y-%m-%d"> birthday;
        Age age;
        rfl::Email email;
        std::vector<Person> children;
    };

    const auto bart = Person{.first_name = "Bart",
                             .birthday = "1987-04-19",
                             .age = 10,
                             .email = "bart@simpson.com"};

    const auto lisa = Person{.first_name = "Lisa",
                             .birthday = "1987-04-19",
                             .age = 8,
                             .email = "lisa@simpson.com"};

    const auto maggie = Person{.first_name = "Maggie",
                               .birthday = "1987-04-19",
                               .age = 0,
                               .email = "maggie@simpson.com"};

    const auto homer =
        Person{.first_name = "Homer",
               .birthday = "1987-04-19",
               .age = 45,
               .email = "homer@simpson.com",
               .children = std::vector<Person>({bart, lisa, maggie})};

    const std::string expected = std::string(
        R"({"firstName":"Homer","lastName":"Simpson","town":"Springfield","birthday":"1987-04-19","age":45,"email":"homer@simpson.com","children":[{"firstName":"Bart","lastName":"Simpson","town":"Springfield","birthday":"1987-04-19","age":10,"email":"bart@simpson.com","children":[]},{"firstName":"Lisa","lastName":"Simpson","town":"Springfield","birthday":"1987-04-19","age":8,"email":"lisa@simpson.com","children":[]},{"firstName":"Maggie","lastName":"Simpson","town":"Springfield","birthday":"1987-04-19","age":0,"email":"maggie@simpson.com","children":[]}]})");

    const auto json_str = rfl::json::write(homer);

    if (json_str != expected) {
        throw std::runtime_error("Expected: " + expected +
                                 ", got: " + json_str);
    }
}
