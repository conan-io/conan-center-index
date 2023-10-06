#include <outcome.hpp>

namespace outcome = OUTCOME_V2_NAMESPACE;

outcome::result<int> test2(int x)
{
  return x;
}

outcome::result<int> test1(int x)
{
  OUTCOME_TRY(test2(x));
  return 0;
}

int main(void)
{
  return test1(5).value();
}
