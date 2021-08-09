#include "effcee/effcee.h"

int main(void) {
  auto match = effcee::Match("foo bar qux", "foo",
                              effcee::Options().SetChecksName("checks"));
  return 0;
}
