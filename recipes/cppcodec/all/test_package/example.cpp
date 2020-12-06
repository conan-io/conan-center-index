#include <cppcodec/base32_crockford.hpp>
#include <cppcodec/base64_rfc4648.hpp>
#include <iostream>

int main() {
  using base32 = cppcodec::base32_crockford;
  using base64 = cppcodec::base64_rfc4648;

  std::vector<uint8_t> decoded = base64::decode("YW55IGNhcm5hbCBwbGVhc3VyZQ==");
  std::cout << "decoded size (\"any carnal pleasure\"): " << decoded.size() << '\n';
  std::cout << base32::encode(decoded) << std::endl; // "C5Q7J833C5S6WRBC41R6RSB1EDTQ4S8"
  return 0;
}

