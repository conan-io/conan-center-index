#include <string>
#include <vector>

#include "OptionParser.h"

using optparse::OptionParser;
using namespace std;

int main(int argc, char *argv[])
{
    OptionParser parser = OptionParser() .description("just an example");

    parser.add_option("-f", "--file") .dest("filename")
                      .help("write report to FILE") .metavar("FILE");
    parser.add_option("-q", "--quiet")
                      .action("store_false") .dest("verbose") .set_default("1")
                      .help("don't print status messages to stdout");

    optparse::Values options = parser.parse_args(argc, argv);
    vector<string> args = parser.args();

    if (options.get("verbose"))
        cout << options["filename"] << endl;
}
