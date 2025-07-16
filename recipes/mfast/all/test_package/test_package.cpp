#include <mfast.h>
#include <mfast/coder/fast_decoder.h>
#include <mfast/exceptions.h>

#include <string>
#include <iostream>

int main() {
  mfast::fast_decoder decoder;
  const std::string encoded = "FOOBAR";

  const char* start = encoded.c_str();
  const char* end = start + encoded.length();

  try {
    mfast::message_cref msg = decoder.decode(start, end);
  }
  catch (boost::exception& e) {
    std::cerr << boost::diagnostic_information(e);
  }

  std::cout << "Test package successful\n";

  return 0;
}
