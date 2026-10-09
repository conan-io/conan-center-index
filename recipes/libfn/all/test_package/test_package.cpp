#include <fn/and_then.hpp>
#include <fn/expected.hpp>
#include <fn/transform.hpp>

#include <cstdlib>

enum class Error {};
using Result = fn::expected<int, Error>;

constexpr auto answer(int seed) noexcept
{
  return Result{seed}                                            //
         | fn::and_then([](int i) -> Result { return {i * 2}; }) //
         | fn::transform([](int i) { return i + 2; });
}

static_assert(answer(20) == Result{42});

int main() { return answer(20) == Result{42} ? EXIT_SUCCESS : EXIT_FAILURE; }
