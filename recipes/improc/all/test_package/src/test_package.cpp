#include <improc/improc.hpp>
#include <string_view>

int main() {
    static_assert(IMPROC_VERSION >= 10003, "improc >= 1.0.3 required");
    std::string_view v = improc::version_string();
    return v.empty() ? 1 : 0;
}
