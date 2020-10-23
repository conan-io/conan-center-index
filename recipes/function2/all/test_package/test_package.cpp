#include <function2/function2.hpp>

int main(int, char **) {

  fu2::unique_function<void(int, int)> fun = [](int /*a*/, int /*b*/) {};

  (void) fun;

  return 0;
}
