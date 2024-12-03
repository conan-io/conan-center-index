#include <boost/coroutine/all.hpp>
#include <iostream>

int main()
{
  boost::coroutines::coroutine<void>::pull_type sink(
    [](boost::coroutines::coroutine<void>::push_type& source) {
      source();
      std::cout << "Testing Boost::Coroutine" << std::endl;
    });
  return 0;
}
