#include "ss/converter.hpp"

int main() {
    auto converter = ss::converter{};

    auto val = converter.convert<int>("5");

    if (val == 5) {
        return 0;
    }
    return 1;
}
