#include "jwt/jwt.hpp"
#include <iostream>

int main() {
  using namespace jwt::params;

  auto key = "secret"; // Secret to use for the algorithm
  // Create JWT object
  jwt::jwt_object obj{algorithm("HS256"), payload({{"some", "payload"}}),
                      secret(key)};

  // Get the encoded string/assertion
  auto enc_str = obj.signature();
  std::cout << enc_str << std::endl;

  // Decode
  auto dec_obj = jwt::decode(enc_str, algorithms({"hs256"}), secret(key));
  std::cout << dec_obj.header() << std::endl;
  std::cout << dec_obj.payload() << std::endl;

  return 0;
}
