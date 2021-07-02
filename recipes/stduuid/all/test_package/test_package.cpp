#include <iostream>
#include <cassert>
#include "uuid.h"

using namespace uuids;
using namespace std::string_literals;

int main() {

    {
        auto str = "47183823-2574-4bfd-b411-99ed177d3e43"s;
        auto guid = uuids::uuid::from_string(str);
        assert(uuids::to_string(guid) == str);
    }

    {
        uuid const guid = uuids::uuid_random_generator{}();
        assert(!guid.is_nil());
        assert(guid.size() == 16);
        assert(guid.version() == uuids::uuid_version::random_number_based);
        assert(guid.variant() == uuids::uuid_variant::rfc);
    }

}
