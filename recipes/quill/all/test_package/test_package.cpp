#include "quill/Quill.h"

int main()
{
    quill::start();
    auto file_handler = quill::file_handler("logfile.log", "w");
    auto my_logger = quill::create_logger("my_logger", std::move(file_handler));

    LOG_INFO(my_logger, "Hello from {}", "Quill");
    LOG_CRITICAL(my_logger, "This is a conan example {}", 1234);
}
