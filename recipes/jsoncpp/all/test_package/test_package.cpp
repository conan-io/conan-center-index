#ifdef WITH_JSONCPP_PREFIX
#include <jsoncpp/json/json.h>
#else
#include <json/json.h>
#endif

#include <iostream>

int main(int argc, char **argv)
{
	Json::Value value("Hello, World");
	std::cout << value.asString() << std::endl;
	return 0;
}
