#include <kj/arena.h>
#include <iostream>


int main() {
   auto arena = kj::Arena(512);
   arena.allocate<int>(1);
   return 0;
}
