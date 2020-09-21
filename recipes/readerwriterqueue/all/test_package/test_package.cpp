#include <moodycamel/readerwriterqueue.h>

int main() {
  moodycamel::ReaderWriterQueue<int> q;
  q.enqueue(42);
  return 0;
}
