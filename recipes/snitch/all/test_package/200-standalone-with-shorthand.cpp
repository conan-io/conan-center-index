#if defined(HEADER_ONLY)
#   define SNITCH_IMPLEMENTATION
#   include <snitch/snitch_all.hpp>
#else
#   include <snitch/snitch_macros_test_case.hpp>
#   include <snitch/snitch_macros_check.hpp>
#endif

TEST_CASE("compiles and runs") {
    REQUIRE(true == !false);
}
