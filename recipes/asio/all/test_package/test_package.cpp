#include <asio.hpp>

int main()
{
	auto && service = asio::io_service{};
	(void)service;
}
