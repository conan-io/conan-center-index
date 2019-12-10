#include <cstdlib>
#include <iostream>
#include <pthread.h>

int main()
{
    pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
    pthread_mutex_init(&mutex, NULL);
    pthread_mutex_lock(&mutex);
    std::cout << "under pthread mutex" << std::endl;
    pthread_mutex_unlock(&mutex);
    pthread_mutex_destroy(&mutex);
    return EXIT_SUCCESS;
}
