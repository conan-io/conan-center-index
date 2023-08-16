#include <univalue.h>

#include <cstdlib>
#include <iostream>

int main(int argc, char *argv[])
{
    UniValue package1(UniValue::VOBJ);
    package1.pushKV("name", "univalue");
    package1.pushKV("number", 1337);
    package1.pushKV("double", 3.14);
    UniValue package2(UniValue::VOBJ);
    package2.pushKV("name", "boost");
    package2.pushKV("bool", true);
    UniValue parents(UniValue::VOBJ);
    parents.pushKV("p1", package1);
    parents.pushKV("p2", package2);

    std::cout << parents.write(2) << std::endl;
    return EXIT_SUCCESS;
}
