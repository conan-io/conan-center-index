#include <uvw.hpp>

int main() {
#ifdef UVW_API_3_0
    uvw::loop::get_default();
#else
    uvw::Loop::getDefault();
#endif
}
