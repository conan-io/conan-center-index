#include <aws/io/io.h>

int main() {
    struct aws_allocator *allocator = aws_default_allocator();
    aws_io_library_init(allocator);
    aws_io_library_clean_up();

    return EXIT_SUCCESS;
}
