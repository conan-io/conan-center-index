#include <cassert>
#include <moodycamel/concurrentqueue.h>
#include <thread>

int main(int argc, char **argv) {
  moodycamel::ConcurrentQueue<int> q;
  return 0;
}
