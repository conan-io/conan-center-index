cmake_minimum_required(VERSION 3.15)
project(conan_wrapper CXX)

if(UNIX AND NOT APPLE)
    find_package(libuuid REQUIRED)
    add_library(uuid ALIAS libuuid::libuuid)
endif()

add_subdirectory(src)

install(TARGETS hscpp hscpp-mem
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
)
install(DIRECTORY src/include/ DESTINATION include)
