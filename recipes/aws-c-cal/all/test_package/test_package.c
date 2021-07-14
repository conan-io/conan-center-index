#include <aws/cal/hash.h>

int main() {
    struct aws_allocator *allocator = aws_default_allocator();
    struct aws_hash *hash = aws_sha256_new(allocator);
    aws_hash_destroy(hash);

    return EXIT_SUCCESS;
}
