#include "Poco/MD5Engine.h"
#include "Poco/DigestStream.h"
#include <iostream>

int main() {
	Poco::MD5Engine md5;
	Poco::DigestOutputStream dos(md5);
	dos << "Hello Conan!";
	dos.close();
	std::cout << "Poco MD5Engine (crypto): "<< Poco::DigestEngine::digestToHex(md5.digest()) << std::endl;
	return 0;
}
