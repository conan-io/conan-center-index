#include <sstream>

#include <cppcmd/CommandInterpreter.hpp>

using namespace cppcmd;
using namespace std;

int main() {
    unsigned int fooCalls = 0;
    unsigned int barCalls = 0;

    stringstream input;
    auto interpreter = CommandInterpreter(input, std::cout);
    interpreter.registerCommand("foo", [&](const auto&, auto&) { fooCalls++; });
    interpreter.registerCommand("bar", [&](const auto&, auto&) { barCalls++; });

    input << "foo\nbar\nundefined\nfoo\n";
    interpreter.run();

    return 0;
}
