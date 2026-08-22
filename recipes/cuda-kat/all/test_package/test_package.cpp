#include <iostream>
#include <kat/tuple.hpp>


int main() {
    auto t = kat::tuple<int>{1};
    static_assert(kat::tuple_size<kat::tuple<int>>::value == 1, "tuple_size<tuple<T>> test failed.");
    if ( kat::get<0>(t) != 1 )
        { throw std::logic_error{""}; }

    return 0;
}

