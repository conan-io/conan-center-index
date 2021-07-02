#include <cassert>

#include <uvw.hpp>

int main() {
    auto loop = uvw::Loop::getDefault();
    assert(loop != nullptr);
}
