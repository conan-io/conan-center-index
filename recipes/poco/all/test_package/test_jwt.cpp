#include "Poco/JWT/Signer.h"
#include "Poco/JWT/Token.h"

#include <string>

using namespace Poco::JSON;
using namespace Poco::JWT;

//JWT: JSON Web Token

int main() {
    // create and sign a JWT
    Token token;
    token.setType("JWT");
    token.setSubject("1234567890");
    token.payload().set("name", std::string("John Doe"));
    token.setIssuedAt(Poco::Timestamp());

	Signer signer("0123456789ABCDEF0123456789ABCDEF");
	std::string jwt_tx = signer.sign(token, Signer::ALGO_HS256);

	std::cout << "json web token: " << jwt_tx << "\n";

    std::string jwt_rx(
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJpYXQiOjE1MTYyMzkwMjIsIm5hbWUiOiJKb2huIERvZSIsInN1YiI6IjEyMzQ1Njc4OTAifQ."
        "qn9G7NwFEOjIh-7hfCUDZA1aJeQmf7I7YvzCBcdenGw");

    Token token_rx = signer.verify(jwt_rx);

    std::cout << "token contents: ";
    token_rx.payload().stringify(std::cout);
    std::cout << "\n";
}
