#include "antlr4-runtime/antlr4-runtime.h"

#include <iostream>

using namespace antlrcpp;
using namespace antlr4;
using namespace std;

int main(int argc, const char *args[])
{
    ifstream ins;
    ins.open(args[1]);
    ANTLRInputStream input(ins);
    return 0;
}