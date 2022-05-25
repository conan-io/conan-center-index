// 200-standalone.cpp

// main() provided by target Catch2::Catch2WithMain

#include CONAN_CATCH_INCLUDE_PATH

TEST_CASE( "compiles and runs" ) {
    REQUIRE( true == !false );
}
