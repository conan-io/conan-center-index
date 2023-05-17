#include <aws/mqtt/mqtt.h>

int main() {
    struct aws_allocator *allocator = aws_default_allocator();
    aws_mqtt_library_init(allocator);
    aws_mqtt_library_clean_up();

    return EXIT_SUCCESS;
}
