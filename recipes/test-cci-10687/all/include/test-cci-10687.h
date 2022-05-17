#pragma once

#ifdef _WIN32
  #define test-cci-10687_EXPORT __declspec(dllexport)
#else
  #define test-cci-10687_EXPORT
#endif

test-cci-10687_EXPORT void test-cci-10687();
