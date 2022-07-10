#include "st_tree.h"
#include <iostream>

int main() {
    st_tree::tree<const char*> t;
    t.insert("Hello");

    t.root().insert(" ");
    t.root().insert("world");

    t.root()[0].insert("!");
    t.root()[1].insert("\n");

    for (st_tree::tree<const char*>::iterator j = t.begin(); j != t.end(); ++j) {
        std::cout << j->data() << std::endl;
    }

    return 0;
}
