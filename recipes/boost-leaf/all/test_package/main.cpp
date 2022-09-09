#include <cstdio>
#include <boost/leaf.hpp>

using namespace boost;

enum custom_error_t
{
  err1,
  err2,
  err3,
};

leaf::result<int> f1()
{
  return 5;
}

leaf::result<int> f2()
{
  return 15;
}

leaf::result<int> g(int a, int b)
{
  int sum = a + b;
  if (sum == 20)
  {
    return leaf::new_error(custom_error_t::err2);
  }
  return sum;
}

int main()
{
  leaf::result<int> r = leaf::try_handle_some(
      []() -> leaf::result<int>
      {
        BOOST_LEAF_AUTO(v1, f1());
        BOOST_LEAF_AUTO(v2, f2());

        return g(v1, v2);
      },
      [](leaf::match<custom_error_t, custom_error_t::err1, custom_error_t::err3>) -> leaf::result<int>
      {
        exit(1);
        return -1;
      },
      [](custom_error_t e) -> leaf::result<int>
      {
        printf("Error value [%d] handled\n", static_cast<int>(e));
        return 17;
      });

  if (r)
  {
    printf("value of r = %d\n", r.value());
  }
  else
  {
    printf("r contains an error!\n");
  }

  return 0;
}
