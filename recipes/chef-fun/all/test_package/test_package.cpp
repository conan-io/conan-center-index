#include <cstdlib>
#include <iostream>
#include "ChefFun/Option.hh"
#include "ChefFun/Either.hh"

using namespace ChefFun;

int main() {
    Option<std::string> os = Option<std::string>::Some( "abc" );
    auto mapped = os.map( []( auto&& n ){ return 2*n.size(); });

    Either<int,std::string> es = Either<int,std::string>::Right( "abc" );
    

    auto n = es
        .matchRight( []( auto&& ss ) -> int { return ss.size(); } )
        .matchLeft( []( auto&& ii ) -> int { return 2*ii; } );

    return EXIT_SUCCESS;
}
