#include <yamail/resource_pool/async/pool.hpp>

#include <iostream>
#include <thread>
#include <memory>

using ofstream_pool = yamail::resource_pool::async::pool<std::unique_ptr<std::ostream>>;
using time_traits = yamail::resource_pool::time_traits;

struct null_buffer : std::streambuf { int overflow(int c) override { return c; } } null_buf;

int main() {
    boost::asio::io_context service;
    ofstream_pool pool(1, 10);
    boost::asio::spawn(service, [&](boost::asio::yield_context yield){
        boost::system::error_code ec;
        auto handle = pool.get_auto_waste(service, yield[ec], time_traits::duration::max());
        if (ec) {
            std::cout << "handle error: " << ec.message() << std::endl;
            return;
        }
        std::cout << "got resource handle" << std::endl;
        if (handle.empty()) {
            auto stream = std::make_unique<std::ostream>(&null_buf);
            if (!stream->good()) {
                return;
            }
            handle.reset(std::move(stream));
        }
        *(handle.get()) << (time_traits::time_point::min() - time_traits::now()).count() << std::endl;
        if (handle.get()->good()) {
            handle.recycle();
        }
    });
    service.run();
}
