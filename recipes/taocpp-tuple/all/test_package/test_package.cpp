// Copyright (c) 2015-2020 Daniel Frey
// Please see LICENSE for license or visit https://github.com/taocpp/tuple/

#include <tao/tuple/tuple.hpp>

#include <cstdlib>
#include <type_traits>

int main() {
   auto t = tao::tuple< int, double, int >();
   auto t2 = tao::tuple< int, double, int >( 1, 2, 3 );
   auto t3( t2 );

   auto t4 = tao::tuple< int, double, int >( 1, 2, 2 );
   auto t5 = tao::tuple< int, double, int >( 1, 2, 4 );

   static_assert( tao::tuple_size< decltype( t ) >::value == 3, "oops" );
   static_assert( tao::tuple_size< decltype( t2 ) >::value == 3, "oops" );
   static_assert( tao::tuple_size< decltype( t3 ) >::value == 3, "oops" );

   return EXIT_SUCCESS;
}
