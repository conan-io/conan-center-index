#include <cstdlib>
#include <iostream>

#include <tao/pegtl.hpp>


struct grammar : tao::pegtl::seq< tao::pegtl::string< 'h', 'e', 'l', 'l', 'o' >, tao::pegtl::eof > {};


int main(void) {
    tao::pegtl::text_view_input in( "hello" );
    tao::pegtl::parse< grammar >( in );
    std::cout << "PEGTL parsed successfully\n";

    return EXIT_SUCCESS;
}
