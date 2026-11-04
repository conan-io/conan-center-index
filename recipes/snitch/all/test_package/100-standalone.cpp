#if defined(HEADER_ONLY)
#   define SNITCH_IMPLEMENTATION
#   include <snitch/snitch_all.hpp>
#else
#   include <snitch/snitch_macros_test_case.hpp>
#   include <snitch/snitch_macros_check.hpp>
#endif

SNITCH_TEST_CASE("compiles and runs") {
    SNITCH_REQUIRE(true == !false);
}
