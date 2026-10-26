#include <tesults/tesults.h>

#include <iostream>
#include <string>

int main() {
    tesults::Case c;
    c.name = "example";
    c.suite = "ExampleSuite";
    c.result = "pass";

    tesults::Data data;
    data.target = "token";
    data.cases.push_back(c);

    std::cout << "tesults-cpp: " << data.cases.size() << " case(s) ready\n";
    return 0;
}
