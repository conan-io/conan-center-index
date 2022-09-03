#include <plf_stack.h>

#include <iostream>

int main() {
    plf::stack<int> i_stack;
    for (int i = 0; i != 100; ++i) {
        i_stack.push(i);
    }

    int total = 0;
    while (!i_stack.empty()) {
        total += i_stack.top();
        i_stack.pop();
    }

    std::cout << "Total: " << total << std::endl;
    return 0;
}
