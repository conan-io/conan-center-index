#include <brigand/brigand.hpp>

using list1 = brigand::list<double, int, char>;
using list2 = brigand::list<long, unsigned char>;
using flat_list = brigand::flatten<brigand::list<list1, list2, short, brigand::list<brigand::list<unsigned long>>>>;


int main() {

    static_assert(
                 std::is_same<flat_list,
                 brigand::list<double, int, char, long, unsigned char, short, unsigned long>>::value,
                 "failed to compile brigand::flatten example");

    return 0;
}
