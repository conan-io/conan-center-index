#include <iostream>
#include <uniscript.hpp>

int main() {
	std::string text = uniscript::to_unicode("<:alpha> <:fracture A>");
	std::string spelled = uniscript::to_uniscript(text);
	bool ok = text == "\xce\xb1 \xf0\x9d\x94\x84" && spelled == "<:alpha> <:fracture A>";
	std::cout << (ok ? "ok   " : "FAIL ") << "C++ " << uniscript::version << ": " << text << " | " << spelled << "\n";
	return !ok;
}
