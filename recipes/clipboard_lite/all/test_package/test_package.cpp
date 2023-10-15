#include <iostream>
#include "Clipboard_Lite.h"

int main(void) {
    auto clipboard = SL::Clipboard_Lite::CreateClipboard()
        ->onText([](const std::string& text) {
            std::cout << text << std::endl;
        })
        ->onImage([&](const SL::Clipboard_Lite::Image& image) {
            std::cout << "onImage Height=" << image.Height << " Width=" << image.Width << std::endl;
        })
        ->run();

    return 0;
}
