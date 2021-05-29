#include <boost/stacktrace.hpp>

#include <iostream>

void f3() {
    std::cout << "==start stacktrace==\n" << boost::stacktrace::stacktrace() << "==end stacktrace==\n";
}

void f2() {
    f3();
}

void f1() {
    f2();
}

#define TEST_STACKTRACE_ADDR2LINE 1
#define TEST_STACKTRACE_BACKTRACE 2
#define TEST_STACKTRACE_BASIC 3
#define TEST_STACKTRACE_NOOP 4
#define TEST_STACKTRACE_WINDBG 5
#define TEST_STACKTRACE_WINDBG_CACHED 6

static const char *stacktrace_impls[] = {
    "addr2line",
    "backtrace",
    "basic",
    "noop",
    "windbg",
    "windbg_cached",
};

int main() {
    int res = 0;

#if !defined TEST_STACKTRACE_IMPL
    std::cerr << "TEST_STACKTRACE_IMPL not defined!\n";
    res = 1;
#else
    std::cerr << "Testing stacktrace_" << stacktrace_impls[TEST_STACKTRACE_IMPL-1] << "...\n";
#   if defined(BOOST_STACKTRACE_USE_ADDR2LINE)
#       if TEST_STACKTRACE_IMPL != TEST_STACKTRACE_ADDR2LINE
            std::cerr << "BOOST_STACKTRACE_USE_ADDR2LINE defined but not testing stacktrace_addr2line\n";
            res = 1;
#       endif
#       if !defined(BOOST_STACKTRACE_ADDR2LINE_LOCATION)
            std::cerr << "error: BOOST_STACKTRACE_ADDR2LINE_LOCATION not defined\n";
            res = 1;
#       endif
#   endif
#   if defined(BOOST_STACKTRACE_USE_BACKTRACE)
#       if TEST_STACKTRACE_IMPL != TEST_STACKTRACE_BACKTRACE
            std::cerr << "BOOST_STACKTRACE_USE_BACKTRACE defined but not testing stacktrace_backtrace\n";
            res = 1;
#       endif
#   endif
#   if defined(BOOST_STACKTRACE_USE_NOOP)
#       if TEST_STACKTRACE_IMPL != TEST_STACKTRACE_NOOP
            std::cerr << "BOOST_STACKTRACE_USE_NOOP defined but not testing stacktrace_noop\n";
            res = 1;
#       endif
#   endif
#   if defined(BOOST_STACKTRACE_USE_WINDBG)
#       if TEST_STACKTRACE_IMPL != TEST_STACKTRACE_WINDBG
            std::cerr << "BOOST_STACKTRACE_USE_WINDBG defined but not testing stacktrace_windbg\n";
            res = 1;
#       endif
#   endif
#   if defined(BOOST_STACKTRACE_USE_WINDBG_CACHED)
#       if TEST_STACKTRACE_IMPL != TEST_STACKTRACE_WINDBG_CACHED
            std::cerr << "BOOST_STACKTRACE_USE_WINDBG_CACHED defined but not testing stacktrace_windbg_cached\n";
            res = 1;
#       endif
#   endif
#endif
    f1();
    return res;
}
