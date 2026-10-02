#include <boost/coroutine/all.hpp>
#include <iostream>

int main()
{
  BOOST_NAMESPACE::coroutines::coroutine<void>::pull_type sink(
    [](BOOST_NAMESPACE::coroutines::coroutine<void>::push_type& source) {
      source();
      std::cout << "Testing Boost::Coroutine" << std::endl;
    });
  return 0;
}
