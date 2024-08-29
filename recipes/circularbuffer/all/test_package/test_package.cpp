#ifdef CIRCULARBUFFER_1_4_0_LATER
#include <CircularBuffer.hpp>
#else
#include <CircularBuffer.h>
#endif

int main() {
    CircularBuffer<int, 256> buffer;

    buffer.push(5);
    buffer.unshift(1);

    return 0;
}
