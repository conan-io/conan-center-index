#if __has_include("bs_thread_pool/BS_thread_pool.hpp")
// Test units for v3.0.0 and newer
#include "./include/BS_thread_pool_test.hpp"
#else
// Test units for v2.0.0
#include "./include/thread_pool_test.hpp"
#endif
