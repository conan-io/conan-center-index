#include "quill/Quill.h"

int main()
{
    quill::start();
    quill::Handler *file_handler = quill::file_handler("logfile.log", "w");
    quill::Logger *my_logger = quill::create_logger("my_logger", file_handler);

    LOG_INFO(my_logger, "Hello from {}", "Quill");
    LOG_CRITICAL(my_logger, "This is a conan example {}", 1234);
}
