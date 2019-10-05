#include <string>
#include <iostream>
#include <amqpcpp.h>

int
main(int argc, char **argv)
{
	const std::string s = "Hello, World!";
	AMQP::ByteBuffer buffer(s.data(), s.size());
	if (buffer.size() == 13)
		std::cout << "Done" << std::endl;
	else
		std::cout << "Wrong buffer of " << buffer.size() << std::endl;
	return 0;
}
