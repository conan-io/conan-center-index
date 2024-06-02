// Copyright (c) 2018-2024 Jean-Louis Leroy
// Distributed under the Boost Software License, Version 1.0.
// See accompanying file LICENSE_1_0.txt
// or copy at http://www.boost.org/LICENSE_1_0.txt)

#include <sstream>

#include <yorel/yomm2/keywords.hpp>

class Animal {
  public:
    virtual ~Animal() {
    }
};

class Dog : public Animal {};
class Cat : public Animal {};

register_classes(Animal, Dog, Cat);

declare_method(
    void, meet, (virtual_<Animal&>, virtual_<Animal&>, std::ostream&));

define_method(void, meet, (Animal&, Animal&, std::ostream& os)) {
    os << "ignore";
}

// Add definitions for specific pairs of animals.
define_method(void, meet, (Dog& dog1, Dog& dog2, std::ostream& os)) {
    os << "wag tail";
}

define_method(void, meet, (Dog& dog, Cat& cat, std::ostream& os)) {
    os << "chase";
}

define_method(void, meet, (Cat& cat, Dog& dog, std::ostream& os)) {
    os << "run";
}

int main() {
    #ifndef NDEBUG
    yorel::yomm2::default_policy::trace_enabled = true;
    #endif

    yorel::yomm2::update();
    Animal&& snoopy = Dog();
    Animal&& felix = Cat();
    std::ostringstream os;
    meet(snoopy, felix, os); // chase

    return os.str() == "chase" ? 0 : 1;
}
