#include <stdio.h>
#include <tinycthread.h>

/* This is the child thread function */
int HelloThread(void * aArg)
{
  (void)aArg;

  printf("Hello world!\n");
  return 0;
}

/* This is the main program (i.e. the main thread) */
int main()
{
  /* Start the child thread */
  thrd_t t;
  if (thrd_create(&t, HelloThread, (void*)0) == thrd_success)
  {
    /* Wait for the thread to finish */
    thrd_join(t, NULL);
  }

  return 0;
}
