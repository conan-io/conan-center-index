#include <iostream>
#include "clipp.h"
using namespace clipp; using std::cout; using std::string;

int main(int argc, char* argv[]) { 
    bool rec = false, utf16 = false;
    string infile = "", fmt = "csv";

    auto cli = (
        value("input file", infile),
        option("-r", "--recursive").set(rec).doc("convert files recursively"),
        option("-o") & value("output format", fmt),
        option("-utf16").set(utf16).doc("use UTF-16 encoding")
    );

    if(!parse(argc, argv, cli)) cout << make_man_page(cli, argv[0]);
}
