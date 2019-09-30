cmake_minimum_required(VERSION 3.5)
project(libpq)

if(NOT CMAKE_SYSTEM_PROCESSOR)
    set(CMAKE_SYSTEM_PROCESSOR ${CMAKE_HOST_SYSTEM_PROCESSOR})
endif()

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

option(USE_OPENSSL "Build libpq with OpenSSL support" OFF)
option(USE_ZLIB "Build libpq with zlib support" OFF)
set(OPENSSL_DEFINE)
if (USE_OPENSSL)
    set(OPENSSL_DEFINE -DUSE_OPENSSL)
endif()

set(CMAKE_STATIC_LIBRARY_PREFIX)
set(CMAKE_SHARED_LIBRARY_PREFIX)
set(CMAKE_INCLUDE_CURRENT_DIR ON)

file(WRITE source_subfolder/src/port/pg_config_paths.h "#define PGBINDIR \"${CONAN_CMAKE_MODULE_PATH}/bin\"\n")
file(APPEND source_subfolder/src/port/pg_config_paths.h "#define PGBINDIR \"${CONAN_CMAKE_MODULE_PATH}/bin\"\n")
file(APPEND source_subfolder/src/port/pg_config_paths.h "#define PGSHAREDIR \"${CONAN_CMAKE_MODULE_PATH}/share/postgresql\"\n")
file(APPEND source_subfolder/src/port/pg_config_paths.h "#define SYSCONFDIR \"${CONAN_CMAKE_MODULE_PATH}/etc/postgresql\"\n")
file(APPEND source_subfolder/src/port/pg_config_paths.h "#define INCLUDEDIR \"${CONAN_CMAKE_MODULE_PATH}/include\"\n")
file(APPEND source_subfolder/src/port/pg_config_paths.h "#define PKGINCLUDEDIR \"${CONAN_CMAKE_MODULE_PATH}/include/postgresql\"\n")
file(APPEND source_subfolder/src/port/pg_config_paths.h "#define INCLUDEDIRSERVER \"${CONAN_CMAKE_MODULE_PATH}/include/postgresql/server\"\n")
file(APPEND source_subfolder/src/port/pg_config_paths.h "#define LIBDIR \"${CONAN_CMAKE_MODULE_PATH}/lib\"\n")
file(APPEND source_subfolder/src/port/pg_config_paths.h "#define PKGLIBDIR \"${CONAN_CMAKE_MODULE_PATH}/lib/postgresql\"\n")
file(APPEND source_subfolder/src/port/pg_config_paths.h "#define LOCALEDIR \"${CONAN_CMAKE_MODULE_PATH}/share/locale\"\n")
file(APPEND source_subfolder/src/port/pg_config_paths.h "#define DOCDIR \"${CONAN_CMAKE_MODULE_PATH}/share/doc/postgresql\"\n")
file(APPEND source_subfolder/src/port/pg_config_paths.h "#define HTMLDIR \"${CONAN_CMAKE_MODULE_PATH}/share/doc/postgresql\"\n")
file(APPEND source_subfolder/src/port/pg_config_paths.h "#define MANDIR \"${CONAN_CMAKE_MODULE_PATH}/share/man\"\n")

file(REMOVE
    source_subfolder/src/include/pg_config.h
    source_subfolder/src/include/pg_config_ext.h
    source_subfolder/src/include/pg_config_os.h
)

file(READ source_subfolder/configure CONFIGURE_FILE)
string(REGEX MATCH "PACKAGE_VERSION='([0-9]+)" _ "${CONFIGURE_FILE}")
set(PG_MAJORVERSION ${CMAKE_MATCH_1})

file(APPEND source_subfolder/src/include/pg_config.h.win32 "#define PG_MAJORVERSION \"${PG_MAJORVERSION}\"\n")
file(APPEND source_subfolder/src/include/pg_config.h.win32 "#ifndef IGNORE_CONFIGURED_SETTINGS\n")
file(APPEND source_subfolder/src/include/pg_config.h.win32 "#define USE_LDAP 1\n")
file(APPEND source_subfolder/src/include/pg_config.h.win32 "#define RELSEG_SIZE 131072\n")
file(APPEND source_subfolder/src/include/pg_config.h.win32 "#define USE_FLOAT4_BYVAL 1\n")
file(APPEND source_subfolder/src/include/pg_config.h.win32 "#define FLOAT4PASSBYVAL true\n")
file(APPEND source_subfolder/src/include/pg_config.h.win32 "#define FLOAT8PASSBYVAL false\n")

set(VAL_CONFIGURE_ZLIB_VALUE "--without-zlib")
if (USE_ZLIB)
    set(VAL_CONFIGURE_ZLIB_VALUE "--with-zlib")
endif()
set(VAL_CONFIGURE_VALUE "#define VAL_CONFIGURE \"--enable-thread-safety --with-ldap ${VAL_CONFIGURE_ZLIB_VALUE}\"")

file(APPEND source_subfolder/src/include/pg_config.h.win32 "${VAL_CONFIGURE_VALUE}\n")
file(APPEND source_subfolder/src/include/pg_config.h.win32 "#define BLCKSZ 8192\n")
file(APPEND source_subfolder/src/include/pg_config.h.win32 "#define BLCKSZ 8192\n")
file(APPEND source_subfolder/src/include/pg_config.h.win32 "#define XLOG_BLCKSZ 8192\n")
file(APPEND source_subfolder/src/include/pg_config.h.win32 "#endif /* IGNORE_CONFIGURED_SETTINGS */\n")


configure_file(source_subfolder/src/include/pg_config.h.win32 include/pg_config.h)
configure_file(source_subfolder/src/include/pg_config_ext.h.win32 include/pg_config_ext.h)
configure_file(source_subfolder/src/include/port/win32.h include/pg_config_os.h)

file(WRITE ${CMAKE_BINARY_DIR}/include/pg_config_paths.h "#define SYSCONFDIR \"\"")


set(pg_port_src
    source_subfolder/src/port/chklocale.c
    source_subfolder/src/port/crypt.c
    source_subfolder/src/port/dirent.c
    source_subfolder/src/port/dirmod.c
    source_subfolder/src/port/erand48.c
    source_subfolder/src/port/fls.c
    source_subfolder/src/port/fseeko.c
    source_subfolder/src/port/getaddrinfo.c
    source_subfolder/src/port/getopt.c
    source_subfolder/src/port/getopt_long.c
    source_subfolder/src/port/getrusage.c
    source_subfolder/src/port/gettimeofday.c
    source_subfolder/src/port/inet_aton.c
    source_subfolder/src/port/inet_net_ntop.c
    source_subfolder/src/port/kill.c
    source_subfolder/src/port/mkdtemp.c
    source_subfolder/src/port/noblock.c
    source_subfolder/src/port/open.c
    source_subfolder/src/port/path.c
    source_subfolder/src/port/pg_crc32c_sb8.c
    source_subfolder/src/port/pg_crc32c_sse42.c
    source_subfolder/src/port/pg_crc32c_sse42_choose.c
    source_subfolder/src/port/pg_strong_random.c
    source_subfolder/src/port/pgcheckdir.c
    source_subfolder/src/port/pgmkdirp.c
    source_subfolder/src/port/pgsleep.c
    source_subfolder/src/port/pgstrcasecmp.c
    source_subfolder/src/port/pqsignal.c
    source_subfolder/src/port/qsort.c
    source_subfolder/src/port/qsort_arg.c
    source_subfolder/src/port/quotes.c
    source_subfolder/src/port/random.c
    source_subfolder/src/port/snprintf.c
    source_subfolder/src/port/sprompt.c
    source_subfolder/src/port/srandom.c
    source_subfolder/src/port/strlcat.c
    source_subfolder/src/port/strlcpy.c
    source_subfolder/src/port/system.c
    source_subfolder/src/port/tar.c
    source_subfolder/src/port/thread.c
    source_subfolder/src/port/win32env.c
    source_subfolder/src/port/win32security.c
    source_subfolder/src/port/win32setlocale.c
)

if (${MSVC_VERSION} GREATER 1800)
    list(APPEND pg_port_src
         source_subfolder/src/port/win32error.c)
endif()

include_directories(source_subfolder/src/include/port/win32 source_subfolder/src/include/port/win32_msvc)

set(pg_backend_src
    source_subfolder/src/common/base64.c
    source_subfolder/src/common/ip.c
    source_subfolder/src/common/md5.c
    source_subfolder/src/common/saslprep.c
    source_subfolder/src/common/scram-common.c
    source_subfolder/src/common/unicode_norm.c
    source_subfolder/src/backend/utils/mb/wchar.c
    source_subfolder/src/backend/utils/mb/encnames.c
)

set(pg_libpq_src
    source_subfolder/src/interfaces/libpq/fe-auth-scram.c
    source_subfolder/src/interfaces/libpq/fe-auth.c
    source_subfolder/src/interfaces/libpq/fe-connect.c
    source_subfolder/src/interfaces/libpq/fe-exec.c
    source_subfolder/src/interfaces/libpq/fe-lobj.c
    source_subfolder/src/interfaces/libpq/fe-misc.c
    source_subfolder/src/interfaces/libpq/fe-print.c
    source_subfolder/src/interfaces/libpq/fe-protocol2.c
    source_subfolder/src/interfaces/libpq/fe-protocol3.c
    source_subfolder/src/interfaces/libpq/fe-secure.c
    source_subfolder/src/interfaces/libpq/libpq-dist.rc
    source_subfolder/src/interfaces/libpq/libpq-events.c
    source_subfolder/src/interfaces/libpq/pqexpbuffer.c
    source_subfolder/src/interfaces/libpq/pthread-win32.c
    source_subfolder/src/interfaces/libpq/win32.c
)

set(pg_libpq_interface
    source_subfolder/src/include/postgres_ext.h
    ${CMAKE_CURRENT_BINARY_DIR}/include/pg_config_ext.h
    ${CMAKE_CURRENT_BINARY_DIR}/include/pg_config.h
    source_subfolder/src/interfaces/libpq/libpq-fe.h
    source_subfolder/src/interfaces/libpq/libpq-events.h
)

set(pg_libpq_catalog_interface
    source_subfolder/src/include/catalog/pg_type.h
    source_subfolder/src/include/catalog/genbki.h
)

if (USE_OPENSSL)
    list(APPEND pg_libpq_src
        source_subfolder/src/interfaces/libpq/fe-secure-openssl.c
        source_subfolder/src/interfaces/libpq/fe-secure-common.c
        )
    list(APPEND pg_backend_src
        source_subfolder/src/common/sha2_openssl.c
        )
else()
    list(APPEND pg_backend_src
        source_subfolder/src/common/sha2.c
        )
endif()

if (USE_ZLIB)
    list(APPEND pg_libpq_src
            source_subfolder/contrib/pgcrypto/pgp-compress.c
        )
endif()

set(DLL_DEF_FILE source_subfolder/src/interfaces/libpq/libpqdll.def)

set(BUILDING_DLL_DEFINE)
if (BUILD_SHARED_LIBS)
    set(BUILDING_DLL_DEFINE, -DBUILDING_DLL)
endif()

add_library(libpq ${pg_port_src} ${pg_backend_src} ${pg_libpq_src} ${DLL_DEF_FILE})
target_compile_definitions(libpq PRIVATE -DFRONTEND -DENABLE_THREAD_SAFETY ${OPENSSL_DEFINE} -D_CRT_SECURE_NO_WARNINGS ${BUILDING_DLL_DEFINE})
target_link_libraries(libpq PUBLIC ${CONAN_LIBS} ws2_32 wldap32 secur32 advapi32 shell32 crypt32)
target_include_directories(libpq PRIVATE source_subfolder/src/include source_subfolder/src/port source_subfolder/src/backend ${CMAKE_BINARY_DIR}/include)

if (NOT BUILD_SHARED_LIBS)
    # we don't need this in shared build, as have .def file)
    set_target_properties(libpq PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

install(TARGETS libpq
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

install(FILES ${pg_libpq_interface} DESTINATION include)
install(DIRECTORY source_subfolder/src/include/libpq DESTINATION include)
install(FILES ${pg_libpq_catalog_interface} DESTINATION include/catalog)
