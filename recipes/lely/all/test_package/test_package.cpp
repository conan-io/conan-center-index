#include <lely/ev/loop.hpp>
#include <lely/io2/linux/can.hpp>
#include <lely/io2/posix/poll.hpp>
#include <lely/io2/sys/io.hpp>

using namespace lely;

int main() {
  auto io_guard = io::IoGuard{};
  auto context  = io::Context{};
  auto poll     = io::Poll{context};

  auto loop = ev::Loop{poll.get_poll()};
  auto exec = loop.get_executor();

  loop.run();
}

