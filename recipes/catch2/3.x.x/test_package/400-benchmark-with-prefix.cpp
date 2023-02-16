#include <catch2/catch_test_macros.hpp>
#include <catch2/benchmark/catch_benchmark.hpp>

unsigned int Factorial( unsigned int number ) {
  return number > 1 ? Factorial(number-1)*number : 1;
}

CATCH_TEST_CASE( "compiles and runs" ) {
   CATCH_BENCHMARK("factorial 25"){
      return Factorial(25);
   };
}
