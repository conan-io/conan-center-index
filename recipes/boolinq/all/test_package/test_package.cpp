#include <boolinq/boolinq.h>

int main() {
  int src[] = {1,2,3,4,5,6,7,8};
  auto dst = boolinq::from(src).where( [](int a) { return a % 2 == 1; })
                               .select([](int a) { return a * 2; })
                               .where( [](int a) { return a > 2 && a < 12; })
                               .toStdVector();

  return 0;
}
