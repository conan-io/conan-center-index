#include <ozo/connection_info.h>
#include <ozo/request.h>
#include <ozo/shortcuts.h>

#include <boost/asio/io_service.hpp>
#include <boost/asio/spawn.hpp>

#include <iostream>

namespace asio = boost::asio;

// adapted from examples/request.cpp
int main(int argc, char **argv) {
    asio::io_context io;
    auto conn_info = ozo::connection_info("!!invalid_connection_string");

    const auto coroutine = [&] (asio::yield_context yield) {
        ozo::rows_of<int> result;
        ozo::error_code ec;
        using namespace ozo::literals;
        using namespace std::chrono_literals;
        const auto connection = ozo::request(conn_info[io], "SELECT 1"_SQL, 1ns, ozo::into(result), yield[ec]);
    };

    asio::spawn(io, coroutine);
    io.run();

    return 0;
}
