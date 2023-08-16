#include <lely/ev/loop.hpp>
#include <lely/io2/linux/can.hpp>
#include <lely/io2/posix/poll.hpp>
#include <lely/io2/sys/io.hpp>

using namespace lely;

int main() {
  io::IoGuard io_guard{};
  io::Context context{};
  io::Poll poll{context};

  ev::Loop loop{poll.get_poll()};

  loop.run();
}
