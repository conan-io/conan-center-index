#include <oup/observable_unique_ptr.hpp>

#include <cassert>

int main() {
    // Non-owning pointer that will outlive the object
    oup::observer_ptr<int> obs_ptr;

    // Don't optimize this out
    assert(obs_ptr.expired());
    assert(obs_ptr == nullptr);

    return 0;
}
