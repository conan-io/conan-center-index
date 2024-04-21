#include <ringbuffer.hpp>

int main() {
    jnk0le::Ringbuffer<const char*, 256> message;

    message.insert("Hello world");

    const char* tmp = nullptr;
    message.remove(tmp);

    return 0;
}
