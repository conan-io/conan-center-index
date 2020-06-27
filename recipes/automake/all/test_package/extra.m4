dnl This file contains a macro to test adding extra include dirs using conan

AC_DEFUN([AUTOMAKE_TEST_PACKAGE_PREREQ],[
    m4_define([CONAN_MACRO_VERSION], [1.3])
    m4_if(m4_version_compare(CONAN_MACRO_VERSION, [$1]),
        -1,
        [m4_fatal([extra.m4 version $1 or higher is required, but ]CONAN_MACRO_VERSION[ found])]
    )
])dnl AUTOMAKE_TEST_PACKAGE_PREREQ

AC_DEFUN([AUTOMAKE_TEST_PACKAGE_HELLO],[
    echo "Hello world from the extra.m4 script!"
    echo "My args were: $*"
])dnl
