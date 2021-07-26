#include <cstdio>
#include <string>
#include <typeinfo>
#include <iostream>

#include <nuple.h>

using nameid_t = nuple< $("name"), char const*, $("id"), int >;

auto get_person ( int i ) { return nameid_t{ "john", i }; }

auto get_person2 ( int id ) {

  return as_nuple( $name("key"), std::string{ "ivan" }, $name("value"), id );
}

int main() {

  nameid_t n[] = { { "alex", 1 }, { "ivan", 2 } };

  for( auto& v : n )
    printf( "name: %s, id: %d\n", get<$("name")>( v ), get<$("id")>( v ) );

  //return as_nuple(...), also using nuple_ns::name_t to get tag name type and print it

  auto p2 = get_person2( 10 );
  using p2_t = decltype( p2 );
  printf( "get_person2 (as_nuple): %s: %s, %s: %d\n",
        nuple_ns::name_t< p2_t, 0 >::value, get<$("key")>( p2 ).data(),
        nuple_ns::name_t< p2_t, 1 >::value, get<$("value")>( p2 ) );


  //return nuple<...>{ ... }

  auto p = get_person( 3 );
  printf( "get_person: tuple size %d, name: %s, id: %d\n", size( p ), get<$("name")>( p ), get<$("id")>( p ) );


  //usual luple mehods work too

  get<0>( p ) = "irene";
  get<int>( p ) = 4;

  printf( "name: %s, id: %d\n", get<$("name")>( p ), get<$("id")>( p ) );

  luple_do( p, []( auto& v ) {
    std::cout << v << ": " << typeid( v ).name() << "; ";
  } );

  //nuple inherits from luple and supports its APIs
  //see GitHub repo for docs and links to online examples: https://github.com/alexpolt/luple
}
