#define BOOST_TEST_MODULE test_package
#include <boost/test/included/unit_test.hpp>
#include <turtle/mock.hpp>

MOCK_CLASS( mock_class )
{
    MOCK_METHOD( method, 2, void( int, const std::string& ) )
};

BOOST_AUTO_TEST_CASE( demonstrates_adding_builtin_constraints )
{
   mock_class c;
   MOCK_EXPECT( c.method ).with( mock::equal( 3 ), mock::equal( "some string" ) );
   MOCK_EXPECT( c.method ).with( 3, "some string" );                               // equivalent to the previous one using short-cuts
}
