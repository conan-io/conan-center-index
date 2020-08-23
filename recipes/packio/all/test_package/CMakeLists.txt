cmake_minimum_required(VERSION 2.8.12)
project(TestPackage CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if (PACKIO_VERSION VERSION_LESS "1.2.0")
    add_executable(main 1.0.x-1.1.x.cpp)
else ()
    add_executable(main 1.2.x.cpp)
endif ()

target_link_libraries(main ${CONAN_LIBS})
set_property(TARGET main PROPERTY CXX_STANDARD 17)
