#include <iostream>
#include <memory>
#include <vector>
#include "whisper.h"


int main() {
    auto context = std::unique_ptr<whisper_context, void(*)(whisper_context*)>(
            whisper_init_from_file("models/for-tests-ggml-base.en.bin"), &whisper_free);

    if (context == nullptr) {
        std::cout << "Failed to initialize whisper context!" << std::endl;
        return 3;
    }

    return EXIT_SUCCESS;
}
