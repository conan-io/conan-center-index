#include <GMFN/GMFN.h>

#include <print>

int main() {
    std::println("K32GetModuleFileName: {}", GMFN::K32GetModuleFileName().value().string());

    return 0;
};