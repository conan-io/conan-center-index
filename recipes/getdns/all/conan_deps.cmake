cmake_minimum_required(VERSION 3.15)
project(cmake_wrapper)

# Wrapper for find_package() that sets variables in the format expected by the project
macro(custom_find_package name)
    find_package(${name} REQUIRED CONFIG
        # Allow only Conan packages
        NO_DEFAULT_PATH
        PATHS ${CMAKE_PREFIX_PATH}
    )
    string(TOUPPER ${name} name_upper)
    set(${name_upper}_FOUND TRUE)
    set(${name_upper}_INCLUDE_DIR ${${name}_INCLUDE_DIR})
    set(${name_upper}_LIBRARIES ${${name}_LIBRARIES})
endmacro()

custom_find_package(OpenSSL)
if(BUILD_LIBEV)
    custom_find_package(Libev)
endif()
if(BUILD_LIBEVENT2)
    custom_find_package(Libevent2)
endif()
if(BUILD_LIBUV)
    custom_find_package(Libuv)
endif()
if(USE_LIBIDN2)
    custom_find_package(Libidn2)
endif()
