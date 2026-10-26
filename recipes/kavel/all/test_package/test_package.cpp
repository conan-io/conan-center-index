#include <iostream>

#include "kavel/kavel.hpp"

int main() {
    // No network call: an empty prompt is refused locally.
    kavel::Result r = kavel::generate("");
    std::cout << "kavel: " << kavel::to_string(r.reason) << "\n";
    return r.reason == kavel::Reason::other ? 0 : 1;
}
