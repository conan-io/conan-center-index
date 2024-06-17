#include <iostream>
#include "Clipboard_Lite.h"

// just compile it, don't execute it.
// clipboard_lite execute `assert()` with false when test_package runs in headless environment.
auto create_impl() {
    auto clipboard = SL::Clipboard_Lite::CreateClipboard()
    ->onText([](const std::string& text) {
        std::cout << text << std::endl;
    })
    ->onImage([&](const SL::Clipboard_Lite::Image& image) {
        std::cout << "onImage Height=" << image.Height << " Width=" << image.Width << std::endl;
    })
    ->run();

    return clipboard;
}

int main(void) {
    auto* create = create_impl;

    return 0;
}
