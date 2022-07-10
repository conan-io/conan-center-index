#include <icc/Component.hpp>
#include <icc/Event.hpp>
#include <icc/Context.hpp>
#include <thread>
#include <icc/os/timer/Timer.hpp>

int main() {
  auto timer = icc::os::Timer::createTimer();
  timer->setInterval(std::chrono::seconds(10));
  timer->enableContinuous();
  timer->start();
  std::this_thread::sleep_for(std::chrono::seconds(25));
  return 0;
}
