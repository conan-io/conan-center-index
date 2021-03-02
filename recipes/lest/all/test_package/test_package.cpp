#include "lest/lest.hpp"


const lest::test specification[] =
{
    CASE( "Empty string has length zero (succeed)" )
    {
        EXPECT( 0 == std::string(  ).length() );
        EXPECT( 0 == std::string("").length() );
    },
};

int main( int argc, char * argv[] )
{
    return lest::run( specification, argc, argv );
}

