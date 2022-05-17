#pragma once

#ifdef _WIN32
  #define test_module_config_EXPORT __declspec(dllexport)
#else
  #define test_module_config_EXPORT
#endif

test_module_config_EXPORT void test_module_config();
