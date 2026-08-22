#include <aws/auth/auth.h>

int main() {
    struct aws_allocator *allocator = aws_default_allocator();
    aws_auth_library_init(allocator);
    aws_auth_library_clean_up();

    return EXIT_SUCCESS;
}
