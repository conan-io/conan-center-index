#include <matchit.h>
#include <iostream>
#include <tuple>

int32_t main() {
  using namespace matchit;
  auto &strm = std::cout;
  constexpr auto v = std::variant<int, float>{4};
  Id<int> i;
  Id<float> f;
  match(v)(
      // clang-format off
        pattern | as<int>(i) = [&]{
            strm << "got int: " << *i;
        },
        pattern | as<float>(f) = [&]{
            strm << "got float: " << *f;
        }
      // clang-format on
  );

  return 0;
}
