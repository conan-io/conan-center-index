#include <GMFN/GMFN.h>

#include <print>

int main() {
    std::println("K32GetModuleFileName: {}",   GMFN::K32GetModuleFileName().value().string());
    std::println("K32GetModuleFileNameEx: {}", GMFN::K32GetModuleFileNameEx().value().string());

    return 0;
};
