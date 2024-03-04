#include <icc/Component.hpp>
#include <icc/Event.hpp>
#include <icc/Context.hpp>
#include <icc/os/timer/Timer.hpp>

#include <thread>

int main() {
  auto timer = icc::os::Timer::createTimer();
  timer->setInterval(std::chrono::milliseconds(100));
  timer->enableContinuous();
  timer->start();
  std::this_thread::sleep_for(std::chrono::seconds(1));
  return 0;
}
