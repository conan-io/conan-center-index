#include <cassert>

#include <uvw.hpp>

int main() {
#ifdef UVW_VERSION_LESS_3_0_0
    auto loop = uvw::Loop::getDefault();
#else
    auto loop = uvw::loop::get_default();
#endif
    assert(loop != nullptr);
}
