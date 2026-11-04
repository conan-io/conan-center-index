#include "rc_ptr/rc_ptr.hpp"

int main() {
    auto first = memory::rc_ptr<int>{new int{24}};
    auto second = first;
}
