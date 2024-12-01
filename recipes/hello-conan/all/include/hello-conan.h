#pragma once

#include <vector>
#include <string>


#ifdef _WIN32
  #define HELLO_CONAN_EXPORT __declspec(dllexport)
#else
  #define HELLO_CONAN_EXPORT
#endif

HELLO_CONAN_EXPORT void hello_conan();
HELLO_CONAN_EXPORT void hello_conan_print_vector(const std::vector<std::string> &strings);
