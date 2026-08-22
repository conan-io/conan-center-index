#include <json/json.h>
#include <iostream>

int main(int argc, char **argv)
{
	Json::Value value("Hello, World");
	std::cout << value.asString() << std::endl;
	return 0;
}
