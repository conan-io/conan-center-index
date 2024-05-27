#include <string>
#include <rfl.hpp>

struct TestStruct {
    int x;
    std::string name;
};

int main(void) {
    for (const auto& f : rfl::fields<TestStruct>()) {
        (void) f.name();
        (void) f.type();
    }
    return 0;
}
