#include <capnp/message.h>
#include <iostream>


int main() {
   capnp::MallocMessageBuilder message;
   std::cout << sizeof(message) << std::endl;
   return 0;
}
