#include <CircularBuffer.h>

int main() {
    auto buffer = CircularBuffer<int, 256> {};

    buffer.push(5);
    buffer.unshift(1);

    return 0;
}
