#include <boost/stacktrace.hpp>

#include <iostream>

#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif

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

bool check_used_defined()
{
    bool success = true;
#if TEST_STACKTRACE_IMPL == TEST_STACKTRACE_ADDR2LINE
#   if !defined(BOOST_STACKTRACE_USE_ADDR2LINE)
        std::cerr << "testing stacktrace_addr2line but BOOST_STACKTRACE_USE_ADDR2LINE not defined\n";
        success = false;
#   endif
#endif
#if TEST_STACKTRACE_IMPL == TEST_STACKTRACE_BACKTRACE
#   if !defined(BOOST_STACKTRACE_USE_BACKTRACE)
        std::cerr << "testing stacktrace_backtrace but BOOST_STACKTRACE_USE_BACKTRACE not defined\n";
        success = false;
#   endif
#endif
#if TEST_STACKTRACE_IMPL == TEST_STACKTRACE_NOOP
#   if !defined(BOOST_STACKTRACE_USE_NOOP)
        std::cerr << "testing stacktrace_noop but BOOST_STACKTRACE_USE_NOOP not defined\n";
        success = false;
#   endif
#endif
#if TEST_STACKTRACE_IMPL == TEST_STACKTRACE_WINDBG
#   if !defined(BOOST_STACKTRACE_USE_WINDBG)
        std::cerr << "testing stacktrace_windbg but BOOST_STACKTRACE_USE_WINDBG not defined\n";
        success = false;
#   endif
#endif
#if TEST_STACKTRACE_IMPL == TEST_STACKTRACE_WINDBG_CACHED
#   if !defined(BOOST_STACKTRACE_USE_WINDBG_CACHED)
        std::cerr << "testing stacktrace_windbg_cached but BOOST_STACKTRACE_USE_WINDBG_CACHED not defined\n";
        success = false;
#   endif
#endif
    return success;
}

bool check_unused_undefined()
{
    bool success = true;
#   if defined(BOOST_STACKTRACE_USE_ADDR2LINE)
#       if TEST_STACKTRACE_IMPL != TEST_STACKTRACE_ADDR2LINE
            std::cerr << "BOOST_STACKTRACE_USE_ADDR2LINE defined but not testing stacktrace_addr2line\n";
            success = false;
#       endif
#       if !defined(BOOST_STACKTRACE_ADDR2LINE_LOCATION)
            std::cerr << "error: BOOST_STACKTRACE_ADDR2LINE_LOCATION not defined\n";
            success = false;
#       endif
#   endif
#   if defined(BOOST_STACKTRACE_USE_BACKTRACE)
#       if TEST_STACKTRACE_IMPL != TEST_STACKTRACE_BACKTRACE
            std::cerr << "BOOST_STACKTRACE_USE_BACKTRACE defined but not testing stacktrace_backtrace\n";
            success = false;
#       endif
#   endif
#   if defined(BOOST_STACKTRACE_USE_NOOP)
#       if TEST_STACKTRACE_IMPL != TEST_STACKTRACE_NOOP
            std::cerr << "BOOST_STACKTRACE_USE_NOOP defined but not testing stacktrace_noop\n";
            success = false;
#       endif
#   endif
#   if defined(BOOST_STACKTRACE_USE_WINDBG)
#       if TEST_STACKTRACE_IMPL != TEST_STACKTRACE_WINDBG
            std::cerr << "BOOST_STACKTRACE_USE_WINDBG defined but not testing stacktrace_windbg\n";
            success = false;
#       endif
#   endif
#   if defined(BOOST_STACKTRACE_USE_WINDBG_CACHED)
#       if TEST_STACKTRACE_IMPL != TEST_STACKTRACE_WINDBG_CACHED
            std::cerr << "BOOST_STACKTRACE_USE_WINDBG_CACHED defined but not testing stacktrace_windbg_cached\n";
            success = false;
#       endif
#   endif
    return success;
}

int main() {
    int res = 0;

#if !defined TEST_STACKTRACE_IMPL
    std::cerr << "TEST_STACKTRACE_IMPL not defined!\n";
    res = 1;
#else
    std::cerr << "Testing stacktrace_" << stacktrace_impls[TEST_STACKTRACE_IMPL-1] << "...\n";
    if (!check_unused_undefined()) {
        res = 1;
    }
    if (!check_used_defined()) {
        res = 1;
    }
#endif
    f1();
    return res;
}
