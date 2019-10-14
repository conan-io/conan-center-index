/* sigc++config.h.  Generated from sigc++config.h.in by configure.  */

/* Define to omit deprecated API from the library. */
#cmakedefine SIGCXX_DISABLE_DEPRECATED

/* Major version number of sigc++. */
#cmakedefine SIGCXX_MAJOR_VERSION

/* Micro version number of sigc++. */
#cmakedefine SIGCXX_MICRO_VERSION

/* Minor version number of sigc++. */
#cmakedefine SIGCXX_MINOR_VERSION

/* Detect Win32 platform */
#ifdef _WIN32
# if defined(_MSC_VER)
#  define SIGC_MSC 1
#  define SIGC_WIN32 1
#  define SIGC_DLL 1
# elif defined(__CYGWIN__)
#  define SIGC_CONFIGURE 1
# elif defined(__MINGW32__)
#  define SIGC_WIN32 1
#  define SIGC_CONFIGURE 1
# else
#  error "libsigc++ config: Unknown win32 architecture (send me gcc --dumpspecs or equiv)"
# endif
#else /* !_WIN32 */
# define SIGC_CONFIGURE 1
#endif /* !_WIN32 */

#ifdef SIGC_MSC
/*
 * MS VC7 Warning 4251 says that the classes to any member objects in an
 * exported class must also be exported.  Some of the libsigc++
 * template classes contain std::list members.  MS KB article 168958 says
 * that it's not possible to export a std::list instantiation due to some
 * wacky class nesting issues, so our only options are to ignore the
 * warning or to modify libsigc++ to remove the std::list dependency.
 * AFAICT, the std::list members are used internally by the library code
 * and don't need to be used from the outside, and ignoring the warning
 * seems to have no adverse effects, so that seems like a good enough
 * solution for now.
 */
# pragma warning(disable:4251)

#cmakedefine SIGC_MSVC_TEMPLATE_SPECIALIZATION_OPERATOR_OVERLOAD 1
#cmakedefine SIGC_NEW_DELETE_IN_LIBRARY_ONLY 1 /* To keep ABI compatibility */
#cmakedefine SIGC_PRAGMA_PUSH_POP_MACRO 1

#if (_MSC_VER < 1900) && !defined (noexcept)
#define _ALLOW_KEYWORD_MACROS 1
#define noexcept _NOEXCEPT
#endif

#else /* SIGC_MSC */

/* does the C++ compiler support the use of a particular specialization when
   calling operator() template methods. */
#cmakedefine SIGC_GCC_TEMPLATE_SPECIALIZATION_OPERATOR_OVERLOAD

/* Define if the non-standard Sun reverse_iterator must be used. */
#cmakedefine SIGC_HAVE_SUN_REVERSE_ITERATOR

/* does the C++ compiler support the use of a particular specialization when
   calling operator() template methods omitting the template keyword. */
#cmakedefine SIGC_MSVC_TEMPLATE_SPECIALIZATION_OPERATOR_OVERLOAD

/* does the C++ preprocessor support pragma push_macro() and pop_macro(). */
#cmakedefine SIGC_PRAGMA_PUSH_POP_MACRO

#endif /* !SIGC_MSC */

#ifdef SIGC_DLL
# if defined(SIGC_BUILD) && defined(_WINDLL)
#  define SIGC_API __declspec(dllexport)
# elif !defined(SIGC_BUILD)
#  define SIGC_API __declspec(dllimport)
# else
#  define SIGC_API
# endif
#else /* !SIGC_DLL */
# define SIGC_API
#endif /* !SIGC_DLL */
