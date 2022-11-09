#include <CircularBuffer.h>

int main() {
    CircularBuffer<int, 256> buffer;

    buffer.push(5);
    buffer.unshift(1);

    return 0;
}
