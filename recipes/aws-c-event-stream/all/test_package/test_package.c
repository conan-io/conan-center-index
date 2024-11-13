#include <aws/common/allocator.h>
#include <aws/event-stream/event_stream.h>

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

int main() {
    uint8_t expected_data[] = {
        0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x05, 0xc2, 0x48, 0xeb, 0x7d, 0x98, 0xc8, 0xff};
    struct aws_allocator *allocator = aws_default_allocator();

    struct aws_event_stream_message message;

    int res = aws_event_stream_message_init(&message, allocator, NULL, NULL);

    if (res != 0) {
        fprintf(stderr, "Failed to init message\n");
    }

    if (sizeof(expected_data) != aws_event_stream_message_total_length(&message)) {
        fprintf(stderr, "length of message is incorrect\n");
        return EXIT_FAILURE;
    }

    const uint8_t *buffer = aws_event_stream_message_buffer(&message);
    size_t i;
    for (i=0; i<sizeof(expected_data); ++i) {
        if (expected_data[i] != buffer[i]) {
            fprintf(stderr, "Error at index %u!\n", i);
        }
    }

    aws_event_stream_message_clean_up(&message);

    return EXIT_SUCCESS;
}
