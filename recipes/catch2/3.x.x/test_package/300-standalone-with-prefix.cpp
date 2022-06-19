#include <catch2/catch_test_macros.hpp>

CATCH_TEST_CASE( "compiles and runs" ) {
    CATCH_REQUIRE( true == !false );
}
