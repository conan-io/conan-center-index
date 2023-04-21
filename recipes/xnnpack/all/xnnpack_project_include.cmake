if(UNIX AND NOT APPLE)
    # This project forces gcc to use C99 with GNU extensions disabled
    # This may cause the `timespec` time (from POSIX) to not be defined
    # at all - the macro below also causes POSIX types to be defined
    # while remaining in C99 mode.
    add_compile_definitions(_DEFAULT_SOURCE)
endif()

if(NOT CMAKE_SYSTEM_PROCESSOR AND CONAN_XNNPACK_SYSTEM_PROCESSOR)
    set(CMAKE_SYSTEM_PROCESSOR ${CONAN_XNNPACK_SYSTEM_PROCESSOR})
endif()

# The XNNPACK CMake scripts don't call find_package, 
# but can work with targets - here we ensure we bring in those
# targets.
find_package(cpuinfo REQUIRED CONFIG)
find_package(pthreadpool REQUIRED CONFIG)
find_package(fp16 REQUIRED CONFIG)
find_package(fxdiv REQUIRED CONFIG)
