#include <aws/common/allocator.h>
#include <aws/sdkutils/sdkutils.h>

int main() {
    struct aws_allocator *allocator = aws_default_allocator();
    aws_sdkutils_library_init(allocator);
    aws_sdkutils_library_clean_up();

    return EXIT_SUCCESS;
}
