#pragma once

#ifdef _WIN32
# ifdef TEST_SHARED_BUILD
#  define TEST_SHARED_API __declspec(dllexport)
# else
#  define TEST_SHARED_API __declspec(dllimport)
# endif
#else
# define TEST_SHARED_API
#endif

TEST_SHARED_API
const char *get_test_shared_text();
