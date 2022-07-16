#include <system_error2.hpp>

int main() {
	system_error2::system_code sc;
	bool isFailure = sc.failure();
}
