#include "addressbook.pb.h"

#include <iostream>

using namespace tutorial;

int main() {
    Person *p = new Person();
    p->set_name("John Smith");
    if (p->IsInitialized()) {
        std::cerr << "ERROR: person is not initialized\n";
        return 1;
    }
    p->set_id(125);
    if (!p->IsInitialized()) {
        std::cerr << "ERROR: person should have been initialized\n";
        return 1;
    }
    return 0;
}
