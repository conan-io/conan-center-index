#include <asio.hpp>

int main()
{
#if __has_include(<asio/io_service.hpp>)
	auto &&service = asio::io_service{};
	(void)service;
#else
	auto &&context = asio::io_context{};
	(void)context;
#endif
}
