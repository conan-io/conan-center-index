#include <asyncpp/task.hpp>
#include <asyncpp/join.hpp>

#include <iostream>
#include <string>

using namespace asyncpp;


task<std::string> message() {
    co_return std::string("async++ installation works.");
}


int main() {
	std::cout << join(message()) << std::endl;
	return 0;
}
