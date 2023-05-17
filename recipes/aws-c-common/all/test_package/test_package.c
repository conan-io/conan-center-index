#include <aws/common/logging.h>

#include <stdio.h>
#include <stdlib.h>

#define LOG_LEVEL AWS_LOG_LEVEL_TRACE

int main() {
    struct aws_logger_standard_options log_options;
    log_options.level = AWS_LL_TRACE;
    log_options.filename = NULL;
    log_options.file = stdout;

    struct aws_logger logger;
    aws_logger_init_standard(&logger, aws_default_allocator(), &log_options);
    aws_logger_set(&logger);
    AWS_LOGF_TRACE(LOG_LEVEL, "This is a %s message", "trace");
    AWS_LOGF_DEBUG(LOG_LEVEL, "This is a %s message", "debug");
    AWS_LOGF_INFO(LOG_LEVEL, "This is an %s message", "info");
    AWS_LOGF_WARN(LOG_LEVEL, "This is a %s message", "warning");
    AWS_LOGF_ERROR(LOG_LEVEL, "This is a %s message", "error");
    AWS_LOGF_FATAL(LOG_LEVEL, "This is a %s message", "fatal");

    aws_logger_clean_up(&logger);

    return EXIT_SUCCESS;
}
