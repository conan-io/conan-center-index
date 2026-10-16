#include <cassert>

#include <poly/yaml.hpp>

int main() {
    auto root = poly::yaml::parse("ok: true");
    assert(root.is_object());
    return 0;
}
