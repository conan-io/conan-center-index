#include <jwt-cpp/jwt.h>

#ifdef JSON_TRAITS_NEEDED
  #ifndef HAS_DEFAULT_TRAITS
    #include "traits/defaults.h"
  #else
    #include <jwt-cpp/traits/kazuho-picojson/defaults.h>
  #endif
#endif

#include <iostream>

int main() {
	auto token = jwt::create()
		.set_issuer("auth0")
		.set_issued_at(std::chrono::system_clock::now())
		.set_expires_at(std::chrono::system_clock::now() + std::chrono::seconds{3600})
		.sign(jwt::algorithm::hs256{"secret"});

	auto decoded = jwt::decode(token);
#ifdef GET_PAYLOAD_JSON
	for(auto& e : decoded.get_payload_json())
		std::cout << e.first << " = " << e.second << std::endl;
#else
    for(auto& e : decoded.get_payload_claims())
		std::cout << e.first << " = " << e.second.to_json() << std::endl;
#endif

	auto verifier = jwt::verify()
		.allow_algorithm(jwt::algorithm::hs256{"secret"})
		.with_issuer("auth0");

	verifier.verify(decoded);
}
