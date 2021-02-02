#include <yamail/resource_pool/async/pool.hpp>

#include <fstream>
#include <iostream>
#include <thread>
#include <memory>

using ofstream_pool = yamail::resource_pool::async::pool<std::unique_ptr<std::ofstream>>;
using time_traits = yamail::resource_pool::time_traits;

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
            auto file = std::make_unique<std::ofstream>("pool.log", std::ios::app);
            if (!file->good()) {
                std::cout << "open file pool.log error: " << file->rdstate() << std::endl;
                return;
            }
            handle.reset(std::move(file));
        }
        *(handle.get()) << (time_traits::time_point::min() - time_traits::now()).count() << std::endl;
        if (handle.get()->good()) {
            handle.recycle();
        }
    });
    service.run();
    return 0;
}
