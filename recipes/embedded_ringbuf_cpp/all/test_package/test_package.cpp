// size_t is needed for RingBufCPP
#include <cstddef>

#include <RingBufCPP.h>

int main() {
    RingBufCPP<int, 5> q;

    q.add(12);

    int tmp;
    q.pull(&tmp);

    return 0;
}
