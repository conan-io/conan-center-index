#include <iostream>
#include <rfl.hpp>
#include <string>

#if defined(CONAN_TEST_WITH_MSGPACK)
#include <rfl/msgpack.hpp>
#endif

struct TestStruct {
    int x;
    std::string name;
};

int main(void) {
    for (const auto& f : rfl::fields<TestStruct>()) {
        (void)f.name();
        (void)f.type();
    }

#if defined(CONAN_TEST_WITH_MSGPACK)
    const auto test = TestStruct{.x = 15, .name = "test_package"};
    std::cout << "msgpack test: ";
    rfl::msgpack::write(test, std::cout) << std::endl;
#endif

    std::cout << "reflectcpp test successful\n";

    return 0;
}
