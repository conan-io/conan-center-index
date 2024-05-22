#include "quill/Backend.h"
#include "quill/Frontend.h"
#include "quill/LogMacros.h"
#include "quill/Logger.h"
#include "quill/sinks/FileSink.h"

#include <utility>

int main()
{
  // Start the backend thread
  quill::BackendOptions backend_options;
  quill::Backend::start(backend_options);

  // Frontend
  auto file_sink = quill::Frontend::create_or_get_sink<quill::FileSink>(
    "example_file_logging.log",
    []()
    {
      quill::FileSinkConfig cfg;
      cfg.set_open_mode('w');
      cfg.set_filename_append_option(quill::FilenameAppendOption::StartDateTime);
      return cfg;
    }(),
    quill::FileEventNotifier{});

  quill::Logger* logger =
    quill::Frontend::create_or_get_logger("root", std::move(file_sink),
                                          "%(time) [%(thread_id)] %(short_source_location:<28) "
                                          "LOG_%(log_level:<9) %(logger:<12) %(message)",
                                          "%H:%M:%S.%Qns", quill::Timezone::GmtTime);

  // set the log level of the logger to debug (default is info)
  logger->set_log_level(quill::LogLevel::Debug);

  LOG_INFO(logger, "log something {}", 123);
  LOG_DEBUG(logger, "something else {}", 456);
}
