#include <cassert>
#include <moodycamel/readerwriterqueue.h>
#include <thread>

int main(int argc, char **argv) {
  moodycamel::ReaderWriterQueue<int> q;
  return 0;
}
