#include "lest/lest_cpp03.hpp"

#define CASE( name ) lest_CASE( specification, name )

using namespace lest;

test_specification specification;

CASE( "Comment converted to bool indicates absence or presence of comment" )
{
    EXPECT( false == bool( comment( "") ) );
    EXPECT(  true == bool( comment("x") ) );
}

int main( int argc, char * argv[] )
{
    return lest::run( specification, argc, argv );
}

