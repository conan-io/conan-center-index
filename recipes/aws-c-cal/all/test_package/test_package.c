#include <aws/cal/cal.h>

int main() {
    struct aws_allocator* allocator = aws_default_allocator();

    struct aws_logger_standard_options options;
    options.level    = AWS_LL_TRACE;
    options.filename = NULL;
    options.file     = stdout;
    struct aws_logger logger;
    aws_logger_init_standard(&logger, allocator, &options);
    aws_logger_set(&logger);

    aws_cal_library_init(allocator);
    aws_cal_library_clean_up();
    aws_logger_clean_up(&logger);

    return EXIT_SUCCESS;
}
