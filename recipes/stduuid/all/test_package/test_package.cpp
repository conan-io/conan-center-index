#include <iostream>
#include <cassert>

#include "uuid.h"

using namespace std::string_literals;

int main() {
    {
        auto str = "47183823-2574-4bfd-b411-99ed177d3e43"s;
        auto guid = uuids::uuid::from_string(str);
        assert(uuids::to_string(guid) == str);
    }

    {
        std::random_device rd;
        auto seed_data = std::array<int, std::mt19937::state_size> {};
        std::generate(std::begin(seed_data), std::end(seed_data), std::ref(rd));
        std::seed_seq seq(std::begin(seed_data), std::end(seed_data));
        std::mt19937 generator(seq);

        uuids::uuid const guid = uuids::uuid_random_generator{generator}();
        assert(!guid.is_nil());
        assert(guid.size() == 16);
        assert(guid.version() == uuids::uuid_version::random_number_based);
        assert(guid.variant() == uuids::uuid_variant::rfc);
    }

    return 0;
}
