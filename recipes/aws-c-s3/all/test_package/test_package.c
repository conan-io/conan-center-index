#include <aws/s3/s3.h>
#include <stdlib.h>

int main() {
    struct aws_allocator *allocator = aws_default_allocator();
    aws_s3_library_init(allocator);
    aws_s3_library_clean_up();

    return EXIT_SUCCESS;
}
