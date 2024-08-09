#include <fstream>
#include "inipp.h"

int main() {
	inipp::Ini<char> ini;
	ini.generate(std::cout);

	ini.default_section(ini.sections["DEFAULT"]);
	ini.interpolate();
	ini.generate(std::cout);

	return 0;
}
