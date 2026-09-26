#include <ste/ste.hpp>

#include <cstdlib>
#include <iostream>

int main() {
    ste::str s{"  my AWESOME name  "};
    const auto pascal = s.NormalizeSpaces().ToPascalCase();
    const auto slug   = ste::ToSlug("Hello, World! 100%");
    std::cout << "pascal=" << pascal << " slug=" << slug << '\n';
    return (pascal == "MyAwesomeName" && slug == "hello-world-100")
        ? EXIT_SUCCESS : EXIT_FAILURE;
}
