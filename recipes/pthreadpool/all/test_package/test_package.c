#include <pthreadpool.h>

int main() {
    pthreadpool_t threadpool = pthreadpool_create(2);
    pthreadpool_destroy(threadpool);
    return 0;
}
