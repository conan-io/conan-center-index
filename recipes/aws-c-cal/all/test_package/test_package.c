#include <aws/cal/cal.h>

int main() {
    struct aws_allocator *allocator = aws_default_allocator();
    aws_cal_library_init(allocator);
    aws_cal_library_clean_up();

    return EXIT_SUCCESS;
}
