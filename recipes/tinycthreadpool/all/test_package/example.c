#include <threadpool.h>
#include <tinycthread.h>
#include <stdio.h>

int main(void) {
  puts("Start Testing!");
  threadpool_t *threadpool = threadpool_create(3, 5, 0);
  printf("Create thread pool: %#x.\n", threadpool);
  if (threadpool){
    int result = threadpool_destroy(threadpool, 0);
    printf("End Testing! result: %d\n", result);
  }
  return 0;
}
