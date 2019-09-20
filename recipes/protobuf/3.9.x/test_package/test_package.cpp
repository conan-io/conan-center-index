#include <cstdlib>
#include <iostream>

#include "addressbook.pb.h"

int main()
{
	std::cout << "Bincrafters\n";

	tutorial::Person p;
	p.set_id(21);
	p.set_name("Bincrafters");
	p.set_email("bincrafters@github.com");

	std::cout << p.SerializeAsString() << "\n";
	return EXIT_SUCCESS;
}
