#if __has_include(<status-code/system_error2.hpp>)
#  include <status-code/system_error2.hpp>
#else
#  include <system_error2.hpp>
#endif

int main() {
	system_error2::system_code sc;
	bool isFailure = sc.failure();
}
