#include <aws/compression/compression.h>

int main() {
    struct aws_allocator *allocator = aws_default_allocator();
    aws_compression_library_init(allocator);
    aws_compression_library_clean_up();

    return EXIT_SUCCESS;
}
