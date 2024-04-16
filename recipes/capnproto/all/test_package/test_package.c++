#include <capnp/message.h>
#include <iostream>


int main() {
   capnp::MallocMessageBuilder message;
   message.allocateSegment(0);
   std::cout << message.sizeInWords() << std::endl;
   return 0;
}
