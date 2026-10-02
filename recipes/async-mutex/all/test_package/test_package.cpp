// Minimal smoke test: acquire and release the async mutex once on a
// single-threaded io_context. Proves the header parses, the Asio transitive
// dependency is wired, and the advertised catseraf::async_mutex target links.

#include <asio/co_spawn.hpp>
#include <asio/detached.hpp>
#include <asio/io_context.hpp>

#include "catseraf/sync/async_mutex.hpp"

#include <cassert>
#include <cstdio>

namespace {

asio::awaitable<void> use_mutex(catseraf::sync::async_mutex& m) {
    auto guard = co_await m.async_lock();
    assert(guard.has_value());
    // `guard` releases the lock when it goes out of scope here.
}

}  // namespace

int main() {
    asio::io_context ioc;
    catseraf::sync::async_mutex m;

    asio::co_spawn(ioc, use_mutex(m), asio::detached);
    ioc.run();

    std::puts("async-mutex test_package OK");
    return 0;
}
