#pragma once

#ifdef _WIN32
  #define test_tool_requires_EXPORT __declspec(dllexport)
#else
  #define test_tool_requires_EXPORT
#endif

test_tool_requires_EXPORT void test_tool_requires();
