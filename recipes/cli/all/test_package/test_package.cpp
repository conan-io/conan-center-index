#include <cli/cli.h>
#include <cli/clifilesession.h>

using namespace cli;
using namespace std;


int main()
{
    auto rootMenu = make_unique< Menu >( "cli" );
    rootMenu -> Insert(
            "hello",
            [](std::ostream& out){ out << "Hello, world\n"; },
            "Print hello world" );

    Cli cli( std::move(rootMenu) );
    cli.ExitAction( [](auto& out){ out << "Goodbye and thanks for all the fish.\n"; } );

    CliFileSession input(cli);

    return 0;
}
