#include <jwt.h>
#include <iostream>

int main(int argc, const char** argv) {
	std::string token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXUyJ9.eyJpc3MiOiJhdXRoMCJ9.AbIJTDMFc7yUa5MhvcP03nJPyCPzZtQcGEp-zWfOkEE";
	auto decoded = jwt::decode(token);

	for(auto& e : decoded.get_payload_claims())
		std::cout << e.first << " = " << e.second.to_json() << std::endl;

	auto token = jwt::create()
		.set_issuer("auth0")
		.set_issued_at(std::chrono::system_clock::now())
		.set_expires_at(std::chrono::system_clock::now() + std::chrono::seconds{3600})
		.sign(jwt::algorithm::hs256{"secret"});

	auto verifier = jwt::verify()
		.allow_algorithm(jwt::algorithm::hs256{"secret"})
		.with_issuer("auth0");

	verifier.verify(token);
}
