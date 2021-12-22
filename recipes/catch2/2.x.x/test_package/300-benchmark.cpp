#include <catch2/catch.hpp>

unsigned int Factorial( unsigned int number ) {
  return number > 1 ? Factorial(number-1)*number : 1;
}

TEST_CASE( "compiles and runs" ) {
   BENCHMARK("factorial 25"){
      return Factorial(25);
   };
}
