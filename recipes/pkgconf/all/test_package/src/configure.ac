AC_INIT([test_package_pkgconf],[1.0])
AC_PREREQ([2.69])

PKG_PREREQ([0.29])
PKG_PROG_PKG_CONFIG
[echo pkg-config executable found at $PKG_CONFIG!]
PKG_CHECK_EXISTS([libexample1],
    [echo "found libexample1 :D"],
    [echo "libexample1 not found :("])
