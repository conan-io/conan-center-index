#include <cstdlib>
#include <iostream>

#include <Application/QuickFAST.h>
#include <Messages/FieldAscii.h>

int main() {
    const auto field = QuickFAST::Messages::FieldAscii::create("Hello, World!");
    std::cout << field->toAscii() << std::endl;

    return EXIT_SUCCESS;
}
