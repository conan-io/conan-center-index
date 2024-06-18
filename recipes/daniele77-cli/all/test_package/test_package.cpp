#include <cli/cli.h>
#include <cli/clifilesession.h>


int main()
{
    // setup cli
    auto rootMenu = std::make_unique<cli::Menu>("cli");

    //create the cli with the root menu
    cli::Cli cli(std::move(rootMenu));
    // global exit action
    cli.ExitAction([](auto& out){ out << "Goodbye and thanks for all the fish.\n";});

    return 0;
}

