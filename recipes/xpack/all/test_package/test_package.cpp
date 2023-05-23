#include <iostream>
#include "xpack/json.h"

using namespace rapidjson;

int main() {
    int number = 1;
    std::string xpack_json = xpack::json::encode(number);
    std::cout << xpack_json << std::endl;
    int number2 = 0;
    xpack::json::decode(xpack_json, number2);
    std::cout << number2 << std::endl;
    return 0;
}
