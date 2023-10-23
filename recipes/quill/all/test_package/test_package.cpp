#include "quill/Quill.h"

int main()
{
    quill::start();
#ifdef QUILL_FILE_HANDLERS_API_V3_3
    auto file_handler = quill::file_handler("logfile.log", []() {
        quill::FileHandlerConfig cfg;
        cfg.set_open_mode('w');
        return cfg;
    }());
#else
    auto file_handler = quill::file_handler("logfile.log", "w");
#endif
    auto my_logger = quill::create_logger("my_logger", std::move(file_handler));

    LOG_INFO(my_logger, "Hello from {}", "Quill");
    LOG_CRITICAL(my_logger, "This is a conan example {}", 1234);
}
