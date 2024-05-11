#include <ringbuffer.hpp>

int main() {
    // older gcc(4.9, 5.3) has a bug for alignas(0)
    // https://gcc.gnu.org/bugzilla/show_bug.cgi?id=69089
    jnk0le::Ringbuffer<const char*, 256, false, 16> message;

    message.insert("Hello world");

    const char* tmp = nullptr;
    message.remove(tmp);

    return 0;
}
