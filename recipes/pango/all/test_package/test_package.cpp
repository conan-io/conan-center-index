#include <iostream>
#include <pango/pangocairo.h>

int main()
{
	std::cout << "pango version: " << pango_version_string() << "\n";
	return 0;
}
