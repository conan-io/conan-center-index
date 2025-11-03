#include <nanobind/nanobind.h>

int add(int a, int b) { return a + b; }

NB_MODULE(conan_test_package, m) {
    m.def("add", &add);
}
