#include <oup/observable_unique_ptr.hpp>

#include <string>
#include <iostream>
#include <cassert>

int main() {
    // Non-owning pointer that will outlive the object
    oup::observer_ptr<std::string> obs_ptr;

    {
        // Sealed (unique) pointer that owns the object
        auto owner_ptr = oup::make_observable_sealed<std::string>("hello");

        // A sealed pointer cannot be copied but it can be moved
        // oup::observable_sealed_ptr<std::string> owner_copied = owner_ptr; // error!
        oup::observable_sealed_ptr<std::string> owner_moved = std::move(owner_ptr); // OK

        // Make the observer pointer point to the object
        obs_ptr = owner_moved;

        // The observer pointer is now valid
        assert(!obs_ptr.expired());

        // It can be used like a regular raw pointer
        assert(obs_ptr != nullptr);
        std::cout << *obs_ptr << std::endl;

        // An observer pointer can be copied and moved
        oup::observer_ptr<std::string> obs_copied = obs_ptr; // OK
        oup::observer_ptr<std::string> obs_moved = std::move(obs_copied); // OK
    }

    // The sealed pointer has gone out of scope, the object is deleted,
    // the observer pointer is now null.
    assert(obs_ptr.expired());
    assert(obs_ptr == nullptr);

    return 0;
}
