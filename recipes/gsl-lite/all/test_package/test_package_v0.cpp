
#include <iostream>

#include <gsl/gsl-lite.hpp>

void printCmdArgs( gsl::span<gsl::zstring const> cmdArgs )
{
    Expects( !cmdArgs.empty() );

    auto argsWithoutExeName = cmdArgs.subspan( 1 );
    for ( auto arg : argsWithoutExeName )
    {
        std::cout << arg << "\n";
    }
}

int main( int argc, char* argv[] )
{
    auto numArgs = gsl::narrow<std::size_t>( argc );
    auto cmdArgs = gsl::make_span( argv, numArgs );
    printCmdArgs( cmdArgs );
}
