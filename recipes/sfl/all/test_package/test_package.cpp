#include <cstdlib>

#include "sfl/small_vector.hpp"
#include "sfl/small_flat_set.hpp"
#include "sfl/small_flat_map.hpp"
#include "sfl/small_flat_multiset.hpp"
#include "sfl/small_flat_multimap.hpp"
#include "sfl/small_unordered_flat_set.hpp"
#include "sfl/small_unordered_flat_map.hpp"
#include "sfl/small_unordered_flat_multiset.hpp"
#include "sfl/small_unordered_flat_multimap.hpp"
#include "sfl/compact_vector.hpp"
#include "sfl/segmented_vector.hpp"

int main() {
    sfl::small_vector<int, 10> v1;
    v1.push_back(123);

    sfl::segmented_vector<int, 10> v2;
    v2.push_back(123);

    return EXIT_SUCCESS;
}
