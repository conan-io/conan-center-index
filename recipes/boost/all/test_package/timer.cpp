// Taken from the Boost examples.
// https://www.boost.org/doc/libs/1_71_0/libs/timer/doc/cpu_timers.html

#include <boost/timer/timer.hpp>
#include <cmath>

int main()
{
  boost::timer::auto_cpu_timer t;

  for (long i = 0; i < 100000000; ++i)
    std::sqrt(123.456L); // burn some time

  return 0;
}
