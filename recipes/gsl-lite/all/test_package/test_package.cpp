
#include <iostream>

#include <gsl-lite/gsl-lite.hpp>

void printCmdArgs( gsl_lite::span<gsl_lite::zstring const> cmdArgs )
{
    gsl_Expects( !cmdArgs.empty() );

    auto argsWithoutExeName = cmdArgs.subspan( 1 );
    for ( auto arg : argsWithoutExeName )
    {
        std::cout << arg << "\n";
    }
}

int main( int argc, char* argv[] )
{
    auto numArgs = gsl_lite::narrow_failfast<std::size_t>( argc );
    auto cmdArgs = gsl_lite::make_span( argv, numArgs );
    printCmdArgs( cmdArgs );
}
