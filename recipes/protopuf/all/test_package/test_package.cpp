#include <array>

#include "protopuf/message.h"

using namespace pp;
using namespace std;

using Student = message<
    uint32_field<"id", 1>, 
    string_field<"name", 3>
>;

using Class = message<
    string_field<"name", 8>, 
    message_field<"students", 3, Student, repeated>
>;

int main() {
    // serialization
    Student twice{123, "twice"}, tom{456, "tom"}, jerry{123456, "jerry"};
    Class   myClass{"class 101", {tom, jerry}};
    myClass["students"_f].push_back(twice);

    array<byte, 64> buffer{};
    auto            bufferEnd = message_coder<Class>::encode(myClass, buffer);

    // deserialization
    auto [yourClass, bufferEnd2] = message_coder<Class>::decode(buffer);


    return 0;
}
