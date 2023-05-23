#include <iostream>

#include <zug/meta.hpp>
#include <zug/util.hpp>

using namespace zug;

int main()
{
    using meta::pack;
    using identity_t = decltype(identity);

    static_assert(output_of_t<identity_t>{} == pack<>{}, "");
    static_assert(output_of_t<identity_t, int>{} == pack<int &&>{}, "");
    static_assert(
        output_of_t<identity_t, int, float>{} == pack<int &&, float &&>{}, "");

    static_assert(output_of_t<identity_t, meta::pack<int, float> >{} ==
                      pack<int &&, float &&>{},
                  "");

    static_assert(output_of_t<identity_t, int &>{} == pack<int &>{}, "");
    static_assert(output_of_t<identity_t, int &, const float &>{} ==
                      pack<int &, const float &>{},
                  "");

    static_assert(output_of_t<identity_t, int &&>{} == pack<int &&>{}, "");
    static_assert(output_of_t<identity_t, const int &&, float &&>{} ==
                      pack<const int &&, float &&>{},
                  "");

    // since we verifed the package usage, we declatre SUCCESS
    // it is a compile time test, so it looks a bit wierd we can only succeed :-O
    // if we fail to use zug, this program won't compile
    std::cout << "zug package test: SUCCSESS\n";
    return 0;
}
