#include <args-parser/all.hpp>

int main()
{
    static const int argc = 2;
    static const char * argv[argc] = {"args-parser.test", "-a"};

    Args::CmdLine cmd(argc, argv);

    try {
        cmd.addArgWithFlagOnly('a');

        cmd.parse();
    }
    catch(const Args::BaseException &)
    {
        return 1;
    }

    if(cmd.isDefined("-a"))
        return 0;
    else
        return 1;
}
