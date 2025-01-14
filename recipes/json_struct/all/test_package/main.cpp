#include "json_struct/json_struct.h"
#include <iostream>

struct MyTestStruct
{
    std::string name;
    unsigned age;
    JS_OBJ(name, age);
};

int main()
{
    MyTestStruct person;
    person.name="Jonh";
    person.age=23;

    std::string person_json = JS::serializeStruct(person);
    std::cout << person_json << std::endl;

    return 0;
}
