#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

void* threadFunc(void* data)
{
	printf("threadFunc() called\n");
	fflush(stdout);
	return NULL;
}

int main()
{
  pthread_t thread;
  if (pthread_create(&thread, NULL, threadFunc, NULL)) {
	  printf("Error creating thread\n");
	  fflush(stdout);
	  return 1;

  }

  if (pthread_join(thread, NULL)) {
	  printf("Error joining thread\n");
	  fflush(stdout);
	  return 2;
  }

  return 0;
}
