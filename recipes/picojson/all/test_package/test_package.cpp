#include <picojson.h>

int main() {
	std::string json{ "{ \"picojson_test\" : { \"number\" : 13, \"array\" : [1, 2, 3] } }" };
	picojson::value json_value;

	std::string error{ picojson::parse(json_value, json) };
	if (error.empty()) {
		std::cout << json_value << std::endl;
		std::cout << "Package test completed successfully";
		return 0;
	}

	std::cout << "Package test completed, errors occurred:" << std::endl;
	std::cerr << error << std::endl;
	return 1;
}
