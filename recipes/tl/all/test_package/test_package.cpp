#include <string>
#include <cassert>
#include <type_traits>


#include "tl/apply.hpp"
#include "tl/casts.hpp"
#include "tl/decay_copy.hpp"
#include "tl/dependent_false.hpp"
#include "tl/integer_sequence.hpp"
#include "tl/make_array.hpp"

std::string append_int(std::string s, int i) {
    return s + std::to_string(i);
}


struct foo {
    int i;
};

enum class e {
    a
};

bool run = false;

struct bar {
    bar() = default;
    bar(const bar&) = default;
    bar(const bar&&) {
        run = true;
    }
};


int main()
{
    auto s = tl::apply(append_int, std::make_tuple("hi ", 42));
    assert (s == "hi 42");

    int i = 42;
    auto f = tl::bit_cast<foo>(i);
    assert (i == f.i);

    auto en = e::a;
    auto c = tl::underlying_cast(en);
    static_assert(std::is_same<decltype(c), int>::value, "wat");
    assert (c == static_cast<int>(en));

    bar a;
    tl::decay_copy(std::move(a));
    assert(run == true);

    static_assert(std::is_same<tl::make_index_sequence<10>,
                               tl::index_sequence<0,1,2,3,4,5,6,7,8,9>>::value,
                  "make_index_sequence test failed");

    static_assert(std::is_same<tl::make_index_range<3,5>, tl::index_sequence<3,4,5,6,7>>::value,
                  "make_index_range test failed");
  
  
    auto arr = tl::make_array(1, 12, 42l);
    static_assert(std::is_same<decltype(arr), std::array<long,3>>::value, "Failed");
    assert(arr[0] == 1);
    assert(arr[1] == 12);
    assert(arr[2] == 42l);
}
