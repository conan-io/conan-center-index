cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(MINGW)
    # Avoid the following link error:
    # undefined reference to `__strcpy_chk'
    link_libraries(ssp)
endif()

add_subdirectory("source_subfolder")
