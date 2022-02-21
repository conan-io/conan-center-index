#include <chrono>
#include <cpp-subprocess/subprocess.hpp>
#include <iostream>
#include <thread>

int main() {
  using namespace subprocess;
  std::mutex m;
  std::thread t([&m]() {
    std::this_thread::sleep_for(std::chrono::seconds(2));

    if (m.try_lock()) {
      std::cerr << "timed out!" << std::endl;
      exit(2);
    }
  });
#ifdef _WIN32
  auto cmd = Popen({"tasklist", "/?"}, shell{false});
#else
  auto cmd = Popen({"echo", "a"}, shell{false});
#endif

  cmd.wait();
  m.lock();
  t.join();

  return 0;
}
