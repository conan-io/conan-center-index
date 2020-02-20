#include <pthread.h>
#include <iostream>

void* threadFunc(void* /*data*/)
{
	std::cout << "threadFunc() called" << std::endl;
	return nullptr;
}

int main(int argc, char **argv)
{
  pthread_t thread;
  if (pthread_create(&thread, nullptr, threadFunc, nullptr)) {
	  std::cout << "Error creating thread" << std::endl;
	  return 1;

  }

  if (pthread_join(thread, nullptr)) {
	  std::cout << "Error joining thread" << std::endl;
	  return 2;
  }

  return 0;
}
