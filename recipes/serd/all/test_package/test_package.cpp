#include <serd/serd.h>

int main() {
    auto dummy = serd_reader_new(SERD_NTRIPLES, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr);
    serd_reader_free(dummy);
    return 0;
}
