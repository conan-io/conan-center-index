#include <iostream>
#include "muparserx/mpParser.h"

using namespace mup;

int main() {
    // Create the parser instance
    ParserX  p;

    // Create an array of mixed type
    Value arr(3, 0);
    arr.At(0) = 2.0;
    arr.At(1) = "this is a string";
}
