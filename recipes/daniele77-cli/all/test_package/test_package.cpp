#include <cli/cli.h>
#include <cli/clifilesession.h>

using namespace cli;
using namespace std;

int main()
{
    // setup cli
    auto rootMenu = make_unique< Menu >( "cli" );
    rootMenu -> Insert(
            "hello",
            [](std::ostream& out){ out << "Hello, world\n"; },
            "Print hello world" );
    rootMenu -> Insert(
            "hello_everysession",
            [](std::ostream&){ Cli::cout() << "Hello, everybody" << std::endl; },
            "Print hello everybody on all open sessions" );
    rootMenu -> Insert(
            "answer",
            [](std::ostream& out, int x){ out << "The answer is: " << x << "\n"; },
            "Print the answer to Life, the Universe and Everything " );
    rootMenu -> Insert(
            "color",
            [](std::ostream& out){ out << "Colors ON\n"; SetColor(); },
            "Enable colors in the cli" );
    rootMenu -> Insert(
            "nocolor",
            [](std::ostream& out){ out << "Colors OFF\n"; SetNoColor(); },
            "Disable colors in the cli" );

    auto subMenu = make_unique< Menu >( "sub" );
    subMenu -> Insert(
            "hello",
            [](std::ostream& out){ out << "Hello, submenu world\n"; },
            "Print hello world in the submenu" );
    subMenu -> Insert(
            "demo",
            [](std::ostream& out){ out << "This is a sample!\n"; },
            "Print a demo string" );

    auto subSubMenu = make_unique< Menu >( "subsub" );
        subSubMenu -> Insert(
            "hello",
            [](std::ostream& out){ out << "Hello, subsubmenu world\n"; },
            "Print hello world in the sub-submenu" );
    subMenu -> Insert( std::move(subSubMenu));

    rootMenu -> Insert( std::move(subMenu) );

    Cli cli( std::move(rootMenu) );
    // global exit action
    cli.ExitAction( [](auto& out){ out << "Goodbye and thanks for all the fish.\n"; } );

    CliFileSession input(cli);
    // for CLI, we have not to require interactive input.
    // input.Start();

    return 0;
}

