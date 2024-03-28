# Set the dependency flags expected by https://github.com/facebook/folly/blob/v2023.12.18.00/CMake/folly-deps.cmake

macro(custom_find_package name var)
    find_package(${name} ${ARGN}
        # Allow only Conan packages
        NO_DEFAULT_PATH
        PATHS ${CMAKE_PREFIX_PATH}
    )
    set(${var}_FOUND TRUE)
    set(${var}_VERSION ${${name}_VERSION})
    set(${var}_VERSION_STRING ${${name}_VERSION_STRING})
    set(${var}_INCLUDE_DIRS ${${name}_INCLUDE_DIRS})
    set(${var}_INCLUDE_DIR ${${name}_INCLUDE_DIR})
    set(${var}_INCLUDE ${${name}_INCLUDE_DIR})
    set(${var}_LIB ${${name}_LIBRARIES})
    set(${var}_LIBRARY ${${name}_LIBRARIES})
    set(${var}_LIBRARIES ${${name}_LIBRARIES})
    set(${var}_DEFINITIONS ${${name}_DEFINITIONS})
endmacro()

custom_find_package(BZip2 BZIP2)
custom_find_package(Backtrace BACKTRACE)
custom_find_package(DoubleConversion DOUBLE_CONVERSION REQUIRED)
custom_find_package(Gflags LIBGFLAGS)
custom_find_package(Glog GLOG)
custom_find_package(LZ4 LZ4)
custom_find_package(LibAIO LIBAIO)
custom_find_package(LibDwarf LIBDWARF)
custom_find_package(LibEvent LIBEVENT REQUIRED)
custom_find_package(LibLZMA LIBLZMA)
custom_find_package(LibUnwind LIBUNWIND)
custom_find_package(LibUring LIBURING)
custom_find_package(Libiberty LIBIBERTY)
custom_find_package(Libsodium LIBSODIUM)
custom_find_package(OpenSSL OPENSSL REQUIRED)
custom_find_package(Snappy SNAPPY)
custom_find_package(ZLIB ZLIB)
custom_find_package(Zstd ZSTD)
custom_find_package(fmt FMT REQUIRED)
