cmake_minimum_required(VERSION 3.4)
project(gcrypt LANGUAGES C)

include(conanbuildinfo.cmake)
include(CheckTypeSize)
include(CheckSymbolExists)
include(CheckIncludeFile)
include(CheckLibraryExists)
conan_basic_setup()

option(USE_AES "aes" ON)
option(USE_ARCFOUR "arcfour" ON)
option(USE_BLAKE2 "blake2" ON)
option(USE_BLOWFISH "blowfish" ON)
option(USE_CAMELLIA "camellia" ON)
option(USE_CAST5 "cast5" ON)
option(USE_CHACHA20 "cache20" ON)
option(USE_CRC "crc" ON)
option(USE_DES "des" ON)
option(USE_DSA "dsa" ON)
option(USE_ECC "ecc" ON)
option(USE_ELGAMAL "elgamal" ON)
option(USE_GOST28147 "gost28147" ON)
option(USE_GOST_R_3411_12 "gostr3411-12" ON)
option(USE_GOST_R_3411_94 "gostr3411-94" ON)
option(USE_IDEA "idea" ON)
option(USE_MD2 "md2" OFF)
option(USE_MD4 "md4" ON)
option(USE_MD5 "md5" ON)
option(USE_RFC2268 "rfc2268" ON)
option(USE_RMD160 "rmd160" ON)
option(USE_RSA "rsa" ON)
option(USE_SALSA20 "salsa20" ON)
option(USE_SCRYPT "scrypt" ON)
option(USE_SEED "seed" ON)
option(USE_SERPENT "serpent" ON)
option(USE_SHA1 "sha1" ON)
option(USE_SHA256 "sha256" ON)
option(USE_SHA3 "sha3" ON)
option(USE_SHA512 "sha512" ON)
option(USE_TIGER "tiger" ON)
option(USE_TWOFISH "twofish" ON)
option(USE_WHIRLPOOL "whirlpool" ON)

set(PACKAGE_NAME "libgcrypt")
set(PACKAGE_TARNAME "libgcrypt")
set(PACKAGE_VERSION "1.8.4")
set(PACKAGE_STRING "libgcrypt 1.8.4")
set(PACKAGE_BUGREPORT "http://bugs.gnupg.org")
set(PACKAGE_URL "")
set(BUILD_REVISION "93775172")
set(BUILD_TIMESTAMP "<none>")
set(PACKAGE "${PACKAGE_NAME}")
set(VERSION "${PACKAGE_VERSION}")
set(VERSION_NUMBER "0x010804")
set(GCRYPT_VERSION "${VERSION}")
set(GCRYPT_VERSION_NUMBER "${VERSION_NUMBER}")
set(LIBGCRYPT_CIPHERS "arcfour blowfish cast5 des aes twofish serpent rfc2268 seed camellia idea salsa20 gost28147 chacha20")
set(LIBGCRYPT_DIGESTS "crc gostr3411-94 md2 md4 md5 rmd160 sha1 sha256 sha512 sha3 tiger whirlpool stribog blake2")
set(LIBGCRYPT_KDFS "s2k pkdf2 scrypt")
set(LIBGCRYPT_PUBKEY_CIPHERS "dsa elgamal rsa ecc")

if(WIN32)
  set(USE_ONLY_8DOT3 1)
  set(HAVE_DRIVE_LETTERS 1)
  set(HAVE_DOSISH_SYSTEM 1)
  set(HAVE_W32_SYSTEM 1)
  set(USE_RNDW32 1)
else()
  set(USE_ONLY_8DOT3 0)
  set(HAVE_DRIVE_LETTERS 0)
  set(HAVE_DOSISH_SYSTEM 0)
  set(HAVE_W32_SYSTEM 0)
  set(USE_RNDW32 0)
endif()

if(WINCE)
  set(HAVE_W32CE_SYSTEM 1)
  set(USE_RNDW32CE 1)
else()
  set(HAVE_W32CE_SYSTEM 0)
  set(USE_RNDW32CE 0)
endif()

if(UNIX)
  set(USE_RNDEGD 1)
  set(USE_RNDUNIX 1)
else()
  set(USE_RNDEGD 0)
  set(USE_RNDUNIX 0)
endif()

set(HAVE_CPU_ARCH_ALPHA 0)
set(HAVE_CPU_ARCH_ARM 0)
set(HAVE_CPU_ARCH_M68K 0)
set(HAVE_CPU_ARCH_MIPS 0)
set(HAVE_CPU_ARCH_PPC 0)
set(HAVE_CPU_ARCH_SPARC 0)
set(HAVE_CPU_ARCH_X86 1)

check_type_size("uint64_t" SIZEOF_UINT64_T)
check_type_size("unsigned int" SIZEOF_UNSIGNED_INT)
check_type_size("unsigned long" SIZEOF_UNSIGNED_LONG)
check_type_size("unsigned long long" SIZEOF_UNSIGNED_LONG_LONG)
check_type_size("unsigned short" SIZEOF_UNSIGNED_SHORT)
check_type_size("void*" SIZEOF_VOID_P)

check_symbol_exists(atexit stdlib.h HAVE_ATEXIT)
check_symbol_exists(__builtin_bswap32 stdlib.h HAVE_BUILTIN_BSWAP32)
check_symbol_exists(__builtin_bswap64 stdlib.h HAVE_BUILTIN_BSWAP64)
check_symbol_exists(__builtin_ctz stdlib.h HAVE_BUILTIN_CTZ)
check_symbol_exists(clock time.h HAVE_CLOCK)
check_symbol_exists(clock_gettime time.h HAVE_CLOCK_GETTIME)
check_symbol_exists(_doprnt stdio.h HAVE_DOPRNT)
check_symbol_exists(sys_siglist signal.h HAVE_DECL_SYS_SIGLIST)
check_symbol_exists(fcntl "unistd.h;fcntl.h" HAVE_FCNTL)
check_symbol_exists(flockfiles stdio.h HAVE_FLOCKFILE)
check_symbol_exists(ftruncate "unistd.h;sys/types.h" HAVE_FTRUNCATE)
check_symbol_exists(gethrtime "sys/time.h" HAVE_GETHRTIME)
check_symbol_exists(getpagesize unistd.h HAVE_GETPAGESIZE)
check_symbol_exists(getpid "sys/types.h;unistd.h" HAVE_GETPID)
check_symbol_exists(getrusage "sys/time.h;sys/resource.h" HAVE_GETRUSAGE)
check_symbol_exists(gettimeofday "sys/time.h" HAVE_GETTIMEOFDAY)
check_symbol_exists(memmove string.h HAVE_MEMMOVE)
check_symbol_exists(mlock "sys/mman.h" HAVE_MLOCK)
check_symbol_exists(mmap "sys/mman.h" HAVE_MMAP)
check_symbol_exists(pth_init pth.h HAVE_PTH)
check_symbol_exists(pthread_mutex_init pthread.h HAVE_PTHREAD)
check_symbol_exists(raise signal.h HAVE_RAISE)
check_symbol_exists(rand stdlib.h HAVE_RAND)
check_symbol_exists(stpcpy string.h HAVE_STPCPY)
check_symbol_exists(strcasecmp strings.h HAVE_STRCASECMP)
check_symbol_exists(strerror string.h HAVE_STRERROR)
check_symbol_exists(stricmp string.h HAVE_STRICMP)
check_symbol_exists(vprintf stdio.h HAVE_VPRINTF)
check_symbol_exists(wait4 "sys/types.h;sys/time.h;sys/resourse.h;sys/wait.h" HAVE_WAIT4)
check_symbol_exists(waitpid "sys/types.h;sys/wait.h" HAVE_WAITPID)
check_symbol_exists(strtoul stdlib.h HAVE_STRTOUL)
check_symbol_exists(syscall "unistd.h;sys/syscall.h" HAVE_SYSCALL)
check_symbol_exists(sysconf unistd.h HAVE_SYSCONF)
check_symbol_exists(syslog syslog.h HAVE_SYSLOG)

check_include_file(dlfcn.h HAVE_DLFCN_H)
check_include_file(inttypes.h HAVE_INTTYPES_H)
check_include_file(memory.h HAVE_MEMORY_H)
check_include_file(stdint.h HAVE_STDINT_H)
check_include_file(stdlib.h HAVE_STDLIB_H)
check_include_file(string.h HAVE_STRING_H)
check_include_file(strings.h HAVE_STRINGS_H)
check_include_file("sys/capability.h" HAVE_SYS_CAPABILITY_H)
check_include_file("sys/mman.h" HAVE_SYS_MMAN_H)
check_include_file("sys/msg.h" HAVE_SYS_MSG_H)
check_include_file("sys/select.h" HAVE_SYS_SELECT_H)
check_include_file("sys/socket.h" HAVE_SYS_SOCKET_H)
check_include_file("sys/stat.h" HAVE_SYS_STAT_H)
check_include_file("sys/types.h" HAVE_SYS_TYPES_H)
check_include_file(unistd.h HAVE_UNISTD_H)
check_include_file(winsock2.h HAVE_WINSOCK2_H)
check_include_file(ws2tcpip.h HAVE_WS2TCPIP_H)
check_include_file(stdio.h STDC_HEADERS)

if(EXISTS "/dev/random")
  set(HAVE_DEV_RANDOM 1)
  set(NAME_OF_DEV_RANDOM "/dev/random")
else()
  set(HAVE_DEV_RANDOM 0)
  set(NAME_OF_DEV_RANDOM "")
endif()

if(EXISTS "/dev/urandom")
  set(NAME_OF_DEV_URANDOM "/dev/urandom")
else()
  set(NAME_OF_DEV_URANDOM "")
endif()

set(USE_GNU_PTH ${HAVE_PTH})
# set(USE_RANDOM_DAEMON 0)
set(USE_RNDLINUX ${HAVE_DEV_RANDOM})
if(${HAVE_SYS_CAPABILITY_H})
  set(USE_CAPABILITIES 1)
else()
  set(USE_CAPABILITIES 0)
endif()

file(COPY
    ${CMAKE_CURRENT_SOURCE_DIR}/mod-source-info.h
    DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/mpi)
#FIXME : support other architectures
if(CMAKE_SIZEOF_VOID_P EQUAL 4)
  file(COPY
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/mpi/generic/mpi-asm-defs.h
    DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/mpi)
endif()
if(CMAKE_SIZEOF_VOID_P EQUAL 8)
  file(COPY
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/mpi/amd64/mpi-asm-defs.h
    DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/mpi)
endif()

add_executable(gost-s-box ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/cipher/gost-s-box.c)

configure_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/config.h.in
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/config.h)

configure_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/gcrypt.h.in
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/src/gcrypt.h)

file(GLOB SOURCES
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/cipher/*.c
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/compat/*.c
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/mpi/*.c
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/mpi/generic/*.c
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/random/*.c
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/src/*.c)

list(REMOVE_ITEM SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/cipher/gost-s-box)
list(REMOVE_ITEM SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/src/getrandom.c)
list(REMOVE_ITEM SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/src/gcryptrnd.c)
list(REMOVE_ITEM SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/src/hwf-arm.c)
list(REMOVE_ITEM SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/src/mpicalc.c)
list(REMOVE_ITEM SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/src/dumpsexp.c)
list(REMOVE_ITEM SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/random/jitterentropy-base.c)
list(REMOVE_ITEM SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/random/random-daemon.c)

if(NOT WIN32)
  list(REMOVE_ITEM SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/compat/clock.c)
  list(REMOVE_ITEM SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/compat/getpid.c)
  list(REMOVE_ITEM SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/random/rndw32.c)
endif()

if(NOT WINCE)
  list(REMOVE_ITEM SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/random/rndw32ce.c)
endif()

if(NOT UNIX)
  list(REMOVE_ITEM SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/random/rndunix.c)
  list(REMOVE_ITEM SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/random/rndlinux.c)
  list(REMOVE_ITEM SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/random/rndegd.c)
endif()

file(GLOB HEADERS
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/cipher/*.h
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/compat/*.h
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/mpi/*.h
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/mpi/generic/*.h
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/random/*.h
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/src/*.h)

add_library(${PROJECT_NAME} ${SOURCES} ${HEADERS} "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/cipher/gost-sb.h")

add_custom_command(
  OUTPUT "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/cipher/gost-sb.h"
  COMMAND gost-s-box gost-sb.h
  WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/cipher")

add_dependencies(${PROJECT_NAME} gost-s-box)

target_include_directories(${PROJECT_NAME} PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/cipher
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/compat
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/mpi
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/random
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/src)

target_link_libraries(${PROJECT_NAME} PRIVATE ${CONAN_LIBS_LIBGPG-ERROR})
target_include_directories(${PROJECT_NAME} PRIVATE ${CONAN_INCLUDE_DIRS_LIBGPG-ERROR})
target_compile_definitions(${PROJECT_NAME} PRIVATE HAVE_CONFIG_H)
set_target_properties(${PROJECT_NAME} PROPERTIES
  PUBLIC_HEADER ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/src/gcrypt.h
  WINDOWS_EXPORT_ALL_SYMBOLS ON)

install(TARGETS ${PROJECT_NAME}
  PUBLIC_HEADER DESTINATION include
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib)
