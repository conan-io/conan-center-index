#include <cstdlib>
#include <iostream>
#include <string>

#include "rfl.hpp"
#include "rfl/Generic.hpp"
#include "rfl/json.hpp"

int main(void) {
    auto person = rfl::Generic::Object();
    person["first_name"] = "John";
    person["last_name"] = "Doe";
    rfl::json::write(person, std::cout) << std::endl;
    return EXIT_SUCCESS;
}
