#include <boost/coroutine/all.hpp>
#include <iostream>

#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif

using namespace boost::coroutines;

void cooperative(coroutine<void>::push_type &sink)
{
  std::cout << "Hello";
  sink();
  std::cout << "world";
}

int main()
{
  coroutine<void>::pull_type source(cooperative);
  std::cout << ", ";
  source();
  std::cout << "!\n";
}
