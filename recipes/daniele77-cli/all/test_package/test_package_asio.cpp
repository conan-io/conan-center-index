#ifdef CLI_EXAMPLES_USE_STANDALONEASIO_SCHEDULER
    #include <cli/standaloneasioscheduler.h>
    #include <cli/standaloneasioremotecli.h>
    namespace cli
    {
        using MainScheduler = StandaloneAsioScheduler;
        using CliTelnetServer = StandaloneAsioCliTelnetServer;
    } // namespace cli
#elif defined(CLI_EXAMPLES_USE_BOOSTASIO_SCHEDULER)
    #include <cli/boostasioscheduler.h>
    #include <cli/boostasioremotecli.h>
    namespace cli
    {
        using MainScheduler = BoostAsioScheduler;
        using CliTelnetServer = BoostAsioCliTelnetServer;
    }
#endif

#include <cli/cli.h>
#include <cli/clilocalsession.h>
#include <cli/filehistorystorage.h>

#include <vector>
#include <algorithm> // std::copy
#include <complex>

using namespace cli;
using namespace std;

static void foo(std::ostream& out, int x) { out << x << std::endl; }

// a custom struct to be used as a user-defined parameter type
struct Bar {
    string to_string() const { return std::to_string(value); }
    friend istream & operator >> (istream &in, Bar& p);
    int value;
};

istream & operator >> (istream& in, Bar& p) { in >> p.value; return in;}

// needed only for generic help, you can omit this
namespace cli { template <> struct TypeDesc<Bar> { static const char* Name() { return "<bar>"; } }; }

// needed only for generic help, you can omit this
namespace cli { template <> struct TypeDesc<complex<double>> { static const char* Name() { return "<complex>"; } }; }

int main() {
    try {
        CmdHandler colorCmd;
        CmdHandler nocolorCmd;

        // setup cli
        auto rootMenu = make_unique<Menu>("cli");

        rootMenu->Insert(
                "free_function",
                foo,
                "Call a free function that echoes the parameter passed" );
        rootMenu->Insert(
                "hello",
                [](std::ostream& out){ out << "Hello, world\n"; },
                "Print hello world" );
        rootMenu->Insert(
                "hello_everysession",
                [](std::ostream&){ Cli::cout() << "Hello, everybody" << std::endl; },
                "Print hello everybody on all open sessions" );

        // create a cli with the given root menu
        Cli cli( std::move(rootMenu));
        // global exit action
        cli.ExitAction( [](auto& out){ out << "Goodbye and thanks for all the fish.\n"; } );
        // std exception custom handler
        cli.StdExceptionHandler(
            [](std::ostream& out, const std::string& cmd, const std::exception& e) {
                out << "Exception caught in cli handler: "
                    << e.what()
                    << " handling command: "
                    << cmd
                    << ".\n";
            }
        );

        MainScheduler scheduler;
        CliLocalTerminalSession localSession(cli, scheduler, std::cout, 200);
        localSession.ExitAction(
            [&scheduler](auto& out) { // session exit action
                out << "Closing App...\n";
                scheduler.Stop();
            }
        );

        // setup server
        CliTelnetServer server(cli, scheduler, 5000);
        // exit action for all the connections
        server.ExitAction( [](auto& out) { out << "Terminating this session...\n"; } );

        // for CLI, we have not to require interactive input.
        // scheduler.Run();

        return 0;
    }
    catch (const std::exception& e) {
        cerr << "Exception caugth in main: " << e.what() << '\n';
    }
    catch (...) {
        cerr << "Unknown exception caugth in main.\n";
    }
    return -1;
}
