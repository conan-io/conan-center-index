cmake_minimum_required(VERSION 3.1)
project(TestPackage CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if (PACKIO_VERSION VERSION_LESS "1.2.0")
    add_executable(main 1.0.x-1.1.x.cpp)
elseif (PACKIO_VERSION VERSION_LESS "2.0.0")
    add_executable(main 1.2.x.cpp)
else ()
    add_executable(main latest.cpp)
endif ()

target_link_libraries(main ${CONAN_LIBS})
set_property(TARGET main PROPERTY CXX_STANDARD 17)
