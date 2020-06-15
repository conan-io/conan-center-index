#include <boost/exception/all.hpp>
#include <iostream>

typedef boost::error_info<struct tag_my_info,int> my_info; //(1)

struct my_error: virtual boost::exception, virtual std::exception { }; //(2)

void f()
{
  throw my_error() << my_info(42); //(3)
}

void g()
{
  try
  {
    f();
  }
  catch(my_error & x )
  {
    if( int const * mi=boost::get_error_info<my_info>(x) )
        std::cerr << "My info: " << *mi;
  }
}

int main()
{
  g();

  return 0;
}
