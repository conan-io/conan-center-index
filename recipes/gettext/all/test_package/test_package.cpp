#include <iostream>
#include <cstdlib>
#include <locale.h>
#include <libintl.h>

int main(int argc, char * const argv[])
{
	if (argc < 2)
		return -1;
	bindtextdomain("conan", argv[1]);
	textdomain("conan");
	setlocale(LC_ALL, "");
	const char * lang = std::getenv("LANG");
	lang = lang ? lang : "";
	std::cout << "hello in " << lang << ": " << gettext("hello") << std::endl;
    return 0;
}
