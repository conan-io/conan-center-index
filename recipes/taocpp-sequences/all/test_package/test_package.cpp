// Copyright (c) 2015-2020 Daniel Frey
// Please see LICENSE for license or visit https://github.com/taocpp/sequences/

#include <cstdlib>
#include <tao/seq/make_integer_sequence.hpp>
#include <tao/seq/min.hpp>

int main() {
   static_assert( tao::seq::min< int, 1 >::value == 1, "oops" );
   static_assert( tao::seq::min< int, 1, 0 >::value == 0, "oops" );
   static_assert( tao::seq::min< int, 0, 1 >::value == 0, "oops" );
   static_assert( tao::seq::min< int, 1, -1 >::value == -1, "oops" );
   static_assert( tao::seq::min< int, -1, 1 >::value == -1, "oops" );
   static_assert( tao::seq::min< int, -1, 1, 2 >::value == -1, "oops" );
   static_assert( tao::seq::min< int, -1, 2, 1 >::value == -1, "oops" );
   static_assert( tao::seq::min< int, 2, -1, 1 >::value == -1, "oops" );
   static_assert( tao::seq::min< int, 0, 1, 2, -1, 1, 0, -1, 1 >::value == -1, "oops" );
   static_assert( tao::seq::min< tao::seq::make_index_sequence< 10 > >::value == 0, "oops" );

   return EXIT_SUCCESS;
}
