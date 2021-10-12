#include <cista.h>

struct pos {
    int x;
    int y;
};

namespace data = cista::offset;
using pos_map = data::hash_map<data::vector<pos>, data::hash_set<data::string>>;

int main() {
    constexpr auto const MODE = cista::mode::WITH_VERSION | cista::mode::WITH_INTEGRITY;

    { // Serialize
        auto positions = pos_map{
            {{{1, 2}, {3, 4}}, {"hello", "cista"}},
            {{{5, 6}, {7, 8}}, {"hello", "world"}},
        };
        cista::buf mmap{cista::mmap{"data"}};
        cista::serialize<MODE>(mmap, positions);
    }

    // Deserialize.
    auto b = cista::mmap("data", cista::mmap::protection::READ);
    auto positions = cista::deserialize<pos_map, MODE>(b);

    return 0;
}
