#include <atomic_queue/atomic_queue.h>

int main(int argc, char* argv[])
{
    atomic_queue::AtomicQueue<int, 1> q;

    const int iPush = 42;
    q.push(iPush);

    const int iPop = q.pop();

    return (iPush - iPop);
}
