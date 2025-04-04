#include <asio.hpp>

int main()
{
#ifdef ASIO_IO_SERVICE
    auto && service = asio::io_service{};
#else
    auto && service = asio::io_context{};
#endif
	(void)service;
}
