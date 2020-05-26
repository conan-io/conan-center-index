#include <pybind11/pybind11.h>

static int add(int i, int j) {
    return i + j;
}

static const char *hello() {
    return "Hello from the C++ world!";
}

PYBIND11_MODULE(test_package, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring

    m.def("add", &add, "A function which adds two numbers");
    m.def("msg", &hello, "A function returning a message");
}
