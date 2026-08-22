#include <plf_queue.h>

#include <iostream>

int main() {
    plf::queue<int> i_queue;
    for (int i = 0; i < 100; ++i) {
        i_queue.push(i);
    }

    int total = 0;
    while (!i_queue.empty()) {
        total += i_queue.front();
        i_queue.pop();
    }

    std::cout << "Total: " << total << std::endl;
    return 0;
}
