#include "glaze/glaze.hpp"
#include "glaze/json/json_ptr.hpp"
#include "glaze/api/impl.hpp"

struct my_struct
{
  int i = 287;
  double d = 3.14;
  std::string hello = "Hello World";
  std::array<uint64_t, 3> arr = { 1, 2, 3 };
};

template <>
struct glz::meta<my_struct> {
   using T = my_struct;
   static constexpr auto value = object(
      "i", &T::i,
      "d", &T::d,
      "hello", &T::hello,
      "arr", &T::arr
   );
};

int main(void) {
    std::string buffer = R"({"i":287,"d":3.14,"hello":"Hello World","arr":[1,2,3]})";
    auto s = glz::read_json<my_struct>(buffer);

    (void)s.d;
    (void)s.hello;
    (void)s.arr;

    return 0;
}
