#include <boost/coroutine/all.hpp>
#include <iostream>

#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif

int main()
{
  boost::coroutines::coroutine<void>::pull_type sink(
    [](boost::coroutines::coroutine<void>::push_type& source) { source(); });
  return 0;
}
