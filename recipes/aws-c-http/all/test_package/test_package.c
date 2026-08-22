#include <aws/http/http.h>

int main() {
    struct aws_allocator *allocator = aws_default_allocator();
    aws_http_library_init(allocator);
    aws_http_library_clean_up();

    return EXIT_SUCCESS;
}
