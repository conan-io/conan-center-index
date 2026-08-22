/* Relocation requires the INSTALLDIR define to end with a path segment that is
 * equal to the final installation for the library file. Note that on Windows
 * the convention is <prefix>/bin while on other platforms it's <prefix>/lib */
#ifdef _WIN32
#define INSTALLDIR "/usr/local/bin"
#else
#define INSTALLDIR "/usr/local/lib"
#endif

#define INSTALLPREFIX "/usr/local"
#define PKGDATADIR "/usr/local/share/enchant"
#define PKGLIBDIR "/usr/local/lib/enchant"
#define SYSCONFDIR "/usr/local/etc"
