#include <uvw.hpp>

int main() {
    auto loop = uvw::Loop::getDefault();
    loop->run();
}
