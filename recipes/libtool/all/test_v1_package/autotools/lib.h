#ifndef TESTLIB_LIB_H
#define TESTLIB_LIB_H

#if defined(_WIN32)
#   define TESTLIB_IMPORT_SHARED __declspec(dllimport)
#   define TESTLIB_EXPORT_SHARED __declspec(dllexport)
#   define TESTLIB_IMPORT_STATIC
#   define TESTLIB_EXPORT_STATIC
#else
#   define TESTLIB_IMPORT_SHARED
#   define TESTLIB_EXPORT_SHARED
#   define TESTLIB_IMPORT_STATIC
#   define TESTLIB_EXPORT_STATIC
#endif

#if defined(LIBTEST_BUILDING)
#   define TESTLIB_SHARED TESTLIB_EXPORT_SHARED
#   define TESTLIB_STATIC TESTLIB_EXPORT_STATIC
#else
#   define TESTLIB_SHARED TESTLIB_IMPORT_SHARED
#   define TESTLIB_STATIC TESTLIB_IMPORT_STATIC
#endif

#if defined(LIBHELLO_STATIC)
#   define TESTLIB_API TESTLIB_STATIC
#else
#   define TESTLIB_API TESTLIB_SHARED
#endif

double my_function(double);

extern TESTLIB_API const int libtestlib_value;

#endif // TESTLIB_LIB_H
