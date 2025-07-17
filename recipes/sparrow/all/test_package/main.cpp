#include <cassert>

#if SPARROW_MAJOR_VERSION == 0
#include <sparrow/builder/builder.hpp>
#else
#include <sparrow/builder.hpp>
#endif

int main(int argc, char **argv) {
  // using initializer_list
  auto arr = sparrow::build({1, 2, 3, 4, 5});
  auto arr5 = sparrow::primitive_array<int>({1, 2, 3, 4, 5});
  assert(arr == arr5);
  return EXIT_SUCCESS;
}
